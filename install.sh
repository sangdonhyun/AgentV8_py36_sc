#!/bin/sh
S_SHELL=`env |grep ^SHELL= | cut -d= -f2`
S_PATH_TMP=`echo $PATH`
scriptdir_tmp=`dirname -- "\$0"`
script_dir=`cd \$scriptdir_tmp && pwd`

echo "#!$S_SHELL
FLETA_HOME=$script_dir
PYTHONHOME=\$FLETA_HOME/python36

PATH=\$FLETA_HOME:\$PYTHONHOME/bin/:/sbin:$S_PATH_TMP
export PATH

OSTYPE=`uname -a |awk '{print \$1}'`

if [ \$OSTYPE = 'Linux' ];then
    LD_LIBRARY_PATH=\${FLETA_HOME}/ssl:\$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH
fi
" > $script_dir/fleta.sh

chmod 755 $script_dir/fleta.sh

. $script_dir/fleta.sh

if [ -f $script_dir/portcheck.py ];then
    b_port_check=`$script_dir/python36/bin/python3 $script_dir/portcheck.py`
else
    b_port_check=False
fi

if [ False = $b_port_check ];then
    sh $script_dir/fletaStart.sh
else
    echo "########################"
    echo "#        ERROR         #"
    echo "#Already TCP Agent Port#"
    echo "########################"
fi
rm -f $script_dir/install.sh