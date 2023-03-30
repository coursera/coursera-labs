# Eclipse Photon IDE Docker Container + Java 8 OpenJDK + Maven 3.6 + Python 3.6 + PIP3 20 + + npm 6 + nodejs v13 + Gradle 6 + VNC/noVNC 

[![](https://images.microbadger.com/badges/image/openkbs/eclipse-docker-vnc.svg)](https://microbadger.com/images/openkbs/eclipse-docker-vnc "Get your own image badge on microbadger.com") [![](https://images.microbadger.com/badges/version/openkbs/eclipse-docker-vnc.svg)](https://microbadger.com/images/openkbs/eclipse-docker-vnc "Get your own version badge on microbadger.com")

# NOTE: This docker default is providing latest Eclipse Photon instead of Oxygen and you can change it to build other versions!!!

# Components
* Eclipse '2020-06' JEE version (you can change if by change Dockerfile)
* Base Components (e.g., Maven, Java, NodeJS, etc.)
  * See [openkbs/jdk-mvn-py3 - Components](https://github.com/DrSnowbird/jdk-mvn-py3/blob/master/README.md#Components)
  * See [openkbs/jdk-mvn-py3 - Releases Information](https://github.com/DrSnowbird/jdk-mvn-py3/blob/master/README.md#Releases-information)

# Run (recommended for easy-start)
Image is pulling from openkbs/eclipse-docker-vnc
```
./run.sh
```

## Mobile devices and Desktop PC supported / tested:
* SmartPhones: tested ok! iPhone5 Safari works though phone screen size being too small vs the desired HD 1920x1080. It should work across all the smartphones with HTML5-capable brwosers. Hence, to access with small phone screen, run with VNC_RESOLUTION=800x600 (or adjust it to fit your phone's screen size)
* Tablets: tested ok! Amazon Fire with noVNC works!. It should work across all the tablets with HTML5-capable brwosers.
![Eclipse Photon on Amazon Fire tablet](doc/eclipse-photon-docker-on-Amazon-Fire-tablet.jpeg).
* Desktop PC or MacBook: tested ok! It should work across all PCs Desktop with HTML5-capable brwosers. ![Eclipse Photon on Desktop PC Browser](doc/eclipse-docker-vnc-on-Desktop-PC-Browser.png)

## Connect to VNC Viewer/Client or noVNC (Browser-based VNC)
* connect via VNC viewer localhost:5901, default password: vncpassword
* connect via noVNC HTML5 full client: http://localhost:6901/vnc.html, default password: vncpassword
* connect via noVNC HTML5 lite client: http://localhost:6901/?password=vncpassword

Once it is up, the default password is "vncpassword" to access with your web browser:
```
http://<ip_address>:6901/vnc.html,
e.g.
=> Standalone Docker: http://localhost:6901/vnc.html
=> Openshift Container Platform: http://<route-from-openshift>/vnc.html
=> similarly for Kubernetes Container Platform: (similar to the Openshift above!)
```
# Run - Override VNC environment variables 
The following VNC environment variables can be overwritten at the docker run phase to customize your desktop environment inside the container. You can change those variables using configurations CLI or Web-GUI with OpenShift, Kubernetes, DC/OS, etc.
```
VNC_COL_DEPTH, default is 24 , e.g., change to 16,
    -e VNC_COL_DEPTH=16
VNC_RESOLUTION, default: 1920x1080 , e.g., change to 1024x800
    -e VNC_RESOLUTION=1280x1024
VNC_PW, default: vncpassword , e.g., change to MySpecial!(Password%)
    -e VNC_PW=MySpecial!(Password%)
```
# Screen (Desktop) Resolution
Two ways to change Screen resolutions.

## 1.) Modify ./run.sh file
```
#VNC_RESOLUTION=1280x1024
VNC_RESOLUTION=1920x1080
```

## 2.) Customize Openshift or Kubernetes container run envionrment
```
Set up, say, VNC_RESOLUTION with value 1920x1280
```

# Base the image to build add-on components

```Dockerfile
FROM openkbs/jdk-mvn-py3-vnc
```

# Build
You can build your own image locally.
Note that the default build docker is "latest" version. 
If you want to build older Eclipse like "oxygen", you can following instruction in next section
```
./build.sh
```

# Build (Older Eclipse, e.g. Oxygen)
Two ways (at least) to build:
## **Recommended**:
If you use command line "'**./build.sh**'", you can modify "'**./.env**' (old filename ./docker.env)" file and then, run "./build.sh" to build image
```
## -- Eclipse versions: photon, oxygen, etc.: -- ##
ECLIPSE_VERSION=photon
or
ECLIPSE_VERSION=oxygen
```
Then, 
```
./build.sh
```

# Configurations (Optional)
If you run "./run.sh" instead of "docker-compose up", you don't have to do anything as below.

* The container uses a default "/workspace" folder. 
* The script "./run.sh" will re-use or create the local folder in your $HOME directory with the path below to map into the docker's internal "/workspace" folder.
```
$HOME/data_docker/eclipse-docker-vnc/workspace
```
The above configuration will ensure all your projects created in the container's "/workspace" being "persistent" in your local folder, "$HOME/data_docker/eclipse-docker-vnc/workspace", for your repetitive restart docker container.


# Distributed Storage
This project provides simple host volumes. For using more advanced storage solutions, there are a few distributed cluster storage options available, e.g., Lustre (popular in HPC), GlusterFS, Ceph, etc.
* [Dockerfiles (CentOS, Fedora, Red Hat) for GlusterFS ](https://github.com/gluster/gluster-containers)
* [GlusterFS Quickstart](https://docs.gluster.org/en/latest/Quick-Start-Guide/Quickstart/)
* [Two Days of Pain or How I Deployed GlusterFS Cluster to Kubernetes](https://blog.lwolf.org/post/how-i-deployed-glusterfs-cluster-to-kubernetes/)
# See Also - Other docker-based IDE
* [openkbs/docker-atom-editor](https://hub.docker.com/r/openkbs/docker-atom-editor/)
* [openkbs/eclipse-photon-docker](https://hub.docker.com/r/openkbs/eclipse-photon-docker/)
* [openkbs/eclipse-docker-vnc](https://hub.docker.com/r/openkbs/eclipse-docker-vnc/)
* [openkbs/eclipse-oxygen-docker](https://hub.docker.com/r/openkbs/eclipse-oxygen-docker/)
* [openkbs/intellj-docker](https://hub.docker.com/r/openkbs/intellij-docker/)
* [openkbs/intellj-vnc-docker](https://hub.docker.com/r/openkbs/intellij-vnc-docker/)
* [openkbs/knime-vnc-docker](https://hub.docker.com/r/openkbs/knime-vnc-docker/)
* [openkbs/netbeans10-docker](https://hub.docker.com/r/openkbs/netbeans10-docker/)
* [openkbs/netbeans](https://hub.docker.com/r/openkbs/netbeans/)
* [openkbs/papyrus-sysml-docker](https://hub.docker.com/r/openkbs/papyrus-sysml-docker/)
* [openkbs/pycharm-docker](https://hub.docker.com/r/openkbs/pycharm-docker/)
* [openkbs/scala-ide-docker](https://hub.docker.com/r/openkbs/scala-ide-docker/)
* [openkbs/sublime-docker](https://hub.docker.com/r/openkbs/sublime-docker/)
* [openkbs/webstorm-docker](https://hub.docker.com/r/openkbs/webstorm-docker/)
* [openkbs/webstorm-vnc-docker](https://hub.docker.com/r/openkbs/webstorm-vnc-docker/)

# Resources - JBoss
* [JBoss Tools Integration Stacks 4.6.0.Final](https://tools.jboss.org/downloads/jbosstools_is/photon/4.6.0.Final.html#update_site)
* [Containerize Teiid linked with MariaDB](https://developer.jboss.org/wiki/QuickstartExampleWithDockerizedTeiid)
* [Teiid Downloads](http://teiid.jboss.org/downloads/)
* [Teiid Designer 11.1 with Eclipse Oxygen](http://teiiddesigner.jboss.org/designer_summary/downloads.html)
* [Teiid Cloud - Data Virtualization Services](http://teiid.io/teiid_cloud/)
* [Deploying Teiid VDB](http://teiid.github.io/teiid-documents/master/content/admin/Deploying_VDBs.html)
* [JBoss Tools Integration Stack 4.6.0.Final](https://tools.jboss.org/downloads/jbosstools_is/photon/4.6.0.Final.html)

# Releases information
```
developer@42b554349d81:~/eclipse-workspace$ /usr/scripts/printVersions.sh 
+ echo JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
+ ls -al /java-8-openjdk-amd64
lrwxrwxrwx 1 root root 33 Mar  2 23:05 /java-8-openjdk-amd64 -> /usr/lib/jvm/java-8-openjdk-amd64
+ echo

+ java -version
openjdk version "1.8.0_252"
OpenJDK Runtime Environment (build 1.8.0_252-8u252-b09-1~18.04-b09)
OpenJDK 64-Bit Server VM (build 25.252-b09, mixed mode)
+ mvn --version
Apache Maven 3.6.3 (cecedd343002696d0abb50b32b541b8a6ba2883f)
Maven home: /usr/apache-maven-3.6.3
Java version: 1.8.0_252, vendor: Private Build, runtime: /usr/lib/jvm/java-8-openjdk-amd64/jre
Default locale: en_US, platform encoding: UTF-8
OS name: "linux", version: "5.3.0-62-generic", arch: "amd64", family: "unix"
+ python -V
Python 2.7.17
+ python3 -V
Python 3.6.9
+ pip --version
pip 20.0.2 from /usr/local/lib/python3.6/dist-packages/pip (python 3.6)
+ pip3 --version
pip 20.0.2 from /usr/local/lib/python3.6/dist-packages/pip (python 3.6)
+ gradle --version

Welcome to Gradle 6.0.1!

Here are the highlights of this release:
 - Substantial improvements in dependency management, including
   - Publishing Gradle Module Metadata in addition to pom.xml
   - Advanced control of transitive versions
   - Support for optional features and dependencies
   - Rules to tweak published metadata
 - Support for Java 13
 - Faster incremental Java and Groovy compilation
 - New Zinc compiler for Scala
 - VS2019 support
 - Support for Gradle Enterprise plugin 3.0

For more details see https://docs.gradle.org/6.0.1/release-notes.html


------------------------------------------------------------
Gradle 6.0.1
------------------------------------------------------------

Build time:   2019-11-18 20:25:01 UTC
Revision:     fad121066a68c4701acd362daf4287a7c309a0f5

Kotlin:       1.3.50
Groovy:       2.5.8
Ant:          Apache Ant(TM) version 1.10.7 compiled on September 1 2019
JVM:          1.8.0_252 (Private Build 25.252-b09)
OS:           Linux 5.3.0-62-generic amd64

+ npm -v
6.14.4
+ node -v
v13.14.0
+ cat /etc/lsb-release /etc/os-release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=18.04
DISTRIB_CODENAME=bionic
DISTRIB_DESCRIPTION="Ubuntu 18.04.4 LTS"
NAME="Ubuntu"
VERSION="18.04.4 LTS (Bionic Beaver)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 18.04.4 LTS"
VERSION_ID="18.04"
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
VERSION_CODENAME=bionic
UBUNTU_CODENAME=bionic
```
