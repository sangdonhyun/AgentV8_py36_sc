#!/bin/sh
argc=$#

##################################
SRM_IP=0.0.0.0
AGENT_HOME=/fsutil/HSRM/fletaAgent

SRM_WEB_PORT=80
SRM_RECV_PORT=54002
AGENT_PORT=54001
##################################

scriptdir_tmp=`dirname -- "$0"`
script_dir=`cd $scriptdir_tmp && pwd`

DEVICE_GET=`echo $1 | tr '[a-z]' '[A-Z]'`

if [ $DEVICE_GET ];
then
    DEVICE=$DEVICE_GET
else
    DEVICE=FS
fi

OS=`uname -a |awk '{print $1}'`
S_SHELL=`env |grep SHELL | cut -d= -f2`

if [ $OS = 'SunOS' ];then
    OS_TMP=`uname -a |grep i86pc|wc -l`
    if [ $OS_TMP -gt 0 ];then
        OS='SunOS_X86'
    else
        OS='SunOS'
    fi
fi

if [ $OS = 'Linux' ];then
    OS_TMP=`uname -a |grep i386|wc -l`
    if [ $OS_TMP -gt 0 ];then
        OS='Linux_X86'
    else
        OS='Linux'
    fi
fi

case $OS in
   SunOS)
       FILENAME=Ag_SunOS_AEV8.tar;;
   AIX)
       FILENAME=Ag_AIX_AEV8.tar;;
   HP-UX)
       FILENAME=Ag_HP-UX_ia64_AEV8.tar;;
   Linux)
       FILENAME=Ag_Linux_AEV8.tar;;
   Linux_X86)
       FILENAME=Ag_Linux_X86_AEV8.tar;;
   SunOS_X86)
       FILENAME=Ag_SunOS_X86_AEV8.tar;;
esac

if [ ! -d $AGENT_HOME ];then
    mkdir -p $AGENT_HOME
fi

if [ -f $FILENAME ];then
    mv $FILENAME $AGENT_HOME/
    cd $AGENT_HOME
    tar -xf $FILENAME
    rm -f $FILENAME
else
    echo "$FILENAME NOT FOUND"
    echo "Check File $FILENAME"
    exit
fi

###########################
# fleta.cfg
###########################
echo "[ftp]
server = $SRM_IP
user = fletaFTP
timeout = 5
pass = MfmNWa/dtZt6SN+m0rbfpg==
port = 21

[socket]
port = $SRM_RECV_PORT
server = $SRM_IP

[systeminfo]
set_device = $DEVICE
diskcheck = WMI

[srm]
srm_port = $SRM_WEB_PORT
srm_ip = $SRM_IP

[COMMON]
agent_ip =
version_check = T
transfer = SOCKET
home_dir = $AGENT_HOME
allow_transfer = Y
agent_port = $AGENT_PORT
transfer_encode = N
agent_execute = 10

[save_dir]
dbinfo.MAN = /data/dbms_spool/
dbinfo.SCH = /data/dbms_spool/
diskinfo.SCH = /data/serverinfo/
diskinfo.MAN = /data/serverinfo/
EMC.CLONE = /data/EMC.CLONE/
SYM.EVENT = /data/symevent/


[log]
log_remove = 30" > $AGENT_HOME/config/fleta.cfg

$S_SHELL $AGENT_HOME/install.sh
sleep 2
$S_SHELL $AGENT_HOME/version.sh
rm -f $script_dir/install_v8.sh

