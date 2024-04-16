#!/bin/bash -x

echo "####################### Components: $(basename $0) ###########################"

#### -------------------------------------------------
#### OS_TYPE=1:Ubuntu, 2:Centos,, 0: OS_TYPE_NOT_FOUND
#### -------------------------------------------------
OS_TYPE=0

REPO_CONF=/etc/apt/apt.conf
ETC_ENV=/etc/environment

function detectOS_alt() {
    os_name="`which yum`"
    if [ "$os_name" = "" ]; then
        os_name="`which apt`"
        if [ "$os_name" = "" ]; then
            OS_TYPE=0
        else
            OS_TYPE=1
        fi
    else
        OS_TYPE=2
    fi
 
}
detectOS_alt

function detectOS() {
    os_name="`cat /etc/os-release | grep -i '^NAME=\"Ubuntu\"' | awk -F= '{print $2}' | tr '[:upper:]' '[:lower:]' |sed 's/"//g' `"
    case ${os_name} in
        ubuntu*)
            OS_TYPE=1
            REPO_CONF=/etc/apt/apt.conf
            ETC_ENV=/etc/environment
            ;;
        centos*)
            OS_TYPE=2
            REPO_CONF=/etc/yum.conf
            ETC_ENV=/etc/environment
            ;;
        *)
            OS_TYPE=0
            REPO_CONF=
            ETC_ENV=
            echo "***** ERROR: Can't detect OS Type (e.g., Ubuntu, Centos)! *****"
            echo "Abort now!"
            exit 9
            ;;
    esac
}

HAS_PROXY=0
function detectProxySetup() {
    proxy_vars="`env | grep -i proxy`"
    if [ ! "${proxy_vars}" = "" ]; then
        HAS_PROXY=1
        echo -e ">>>> $0: Found proxy environment vars setup found! \n Setup ${REPO_CONF} & ${ETC_ENV} for proxy servers URLs!"
    else
        echo -e ">>>> $0: No proxy vars setup found! \n No need to setup ${REPO_CONF} & ${ETC_ENV} for proxy servers URLs!"
        exit 0
    fi
}
detectProxySetup

#### ---- Remove extra dobule quote ---- ####
http_proxy=${http_proxy//\"/}
https_proxy=${https_proxy//\"/}
ftp_proxy=${ftp_proxy//\"/}

#### ---- Format (Ubuntu): /etc/apt/apt.conf Proxy Server URL ---- ####
#    Acquire::http::Proxy "http://user:pass@proxy_host:port";
# Other way:
#    sudo apt-get -o Acquire::http::proxy=false <update/install> 
#    sudo apt-get -o Acquire::http::proxy=http://proxy.openkbs.org:80/ <update/install> 
function addProxyToAptConf() {
    echo "================= Setup apt/yum Proxy ===================="
    proxy_already="`cat ${REPO_CONF}|grep -i proxy`"
    if [ "${proxy_already}" = "" ] && [ ${HAS_PROXY} -gt 0 ]; then
        [ ! -z "${http_proxy}" ] && echo "Acquire::http::Proxy \"${http_proxy}\";" | sudo tee -a ${REPO_CONF}
        [ ! -z "${https_proxy}" ] && echo "Acquire::https::Proxy \"${https_proxy}\";" | sudo tee -a ${REPO_CONF}
        [ ! -z "${ftp_proxy}" ] && echo "Acquire::ftp::Proxy \"${ftp_proxy}\";" | sudo tee -a ${REPO_CONF}
    fi
}
addProxyToAptConf ${http_proxy}

function addProxyToEtcEnv() {
    echo "================= Setup System /etc/environment Proxy ===================="
    etc_proxy_already="`cat ${ETC_ENV}|grep -i proxy`"
    if [ "${etc_proxy_already}" = "" ] && [ ${HAS_PROXY} -gt 0 ]; then
        no_proxy=${no_proxy//[[:blank:]]/}
        no_proxy=${no_proxy//\"/}
        [ ! -z "${http_proxy}" ] && echo "http_proxy=${http_proxy}" | sudo tee -a ${ETC_ENV}
        [ ! -z "${https_proxy}" ] && echo "https_proxy=${https_proxy}" | sudo tee -a ${ETC_ENV}
        [ ! -z "${ftp_proxy}" ] && echo "ftp_proxy=${ftp_proxy}" | sudo tee -a ${ETC_ENV}
        [ ! -z "${no_proxy}" ] && echo "no_proxy=${no_proxy}" | sudo tee -a ${ETC_ENV}
    fi
}
addProxyToEtcEnv

function setupNpmProxy() {
    echo "================= Setup NPM Proxy ===================="
    if [ ${HAS_PROXY} -gt 0 ] && [ "`which npm`" != "" ]; then
        npm config set proxy ${http_proxy} 
        npm config set http_proxy ${http_proxy} 
        npm config set https_proxy ${https_proxy} 
        npm config set no_proxy ${no_proxy}
    fi
}
setupNpmProxy ${http_proxy}


