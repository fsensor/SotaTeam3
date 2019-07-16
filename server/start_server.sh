#!/bin/bash

# Find path to this script

if [ "$(echo $0 | grep -E -o '^\./')" == "./" ]
then
  absolute_path=$PWD/$(echo $0 | sed -E '{s/[^\/]+$//}' | sed -E '{s/^\.\///}')
else
  absolute_path=$(echo $0 | sed -E '{s/[^\/]+$//}')
fi

NODE_PATH=node-v12.6.0-linux-x64/bin
APP_DIR=sotaserver
export PATH=$absolute_path$NODE_PATH:$PATH
cd $absolute_path$APP_DIR

function showUsage {
  echo "usage: " $(echo $0 | grep -E -o '[^\/]+$') "[option]"
  echo "  option : d   run as daemon"
}

run_as_daemon=

function checkOption {
  for option in "$@"
  do
    echo process option $option
    if [[ $option == "d" ]]
    then
      run_as_daemon=1
    else
     showUsage
      exit
    fi
  done
  echo 
}

if [ $# -ge 1 ]
then
  checkOption $@
fi

slc start 
