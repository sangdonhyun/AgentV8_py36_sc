#!/bin/sh
#===========================================#
scriptdir_tmp=`dirname -- "$0"`
script_dir=`cd $scriptdir_tmp && pwd`
#===========================================#
. $script_dir/fleta.sh
$script_dir/python27/bin/python $script_dir/fleta_daemon.pyc stop Schedule
nohup $script_dir/python27/bin/python -u $script_dir/fleta_daemon.pyc start Schedule & >> $script_dir/logs/nohup.log 2>&1
sh $script_dir/version.sh