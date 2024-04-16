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


