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
  echo "  option : nopm   no process manager. run using npm directly"
  echo "  option : nodbi   don't init db"
}

run_as_daemon=0
init_db=1

function checkOption {
  for option in "$@"
  do
    echo process option $option
    if [[ $option == "nopm" ]]
    then
      run_as_daemon=1
    elif [[ $option == "nodbi" ]]
    then
      init_db=0
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

if [ $init_db -eq 1 ]
then
echo "Init data base"
cd tools
./initmogodb.sh ii=../../data/initial_db_data/imagemeta.json ht=127.0.0.1 pt=27017 db=imageMeta
cd ..
fi


if [ $run_as_daemon -eq 1 ]
then
  nohup npm start&
else
  slc start 
fi
