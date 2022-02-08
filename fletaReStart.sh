#!/bin/sh
#===========================================#
scriptdir_tmp=`dirname -- "$0"`
script_dir=`cd $scriptdir_tmp && pwd`
#===========================================#
. $script_dir/fleta.sh
cd $script_dir
$script_dir/venv_py/bin/python3 $script_dir/fleta_daemon.pyc stop all
$script_dir/venv_py/bin/python3 -u $script_dir/fleta_daemon.pyc start all
