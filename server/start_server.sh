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
  echo "  option : nopmd  no process manager. run using npm directly in background"
  echo "  option : nodbi  don't init db"
  echo "  option : dbn=db_name specify db name to use."
  echo "  option : dbp=port    specify db port to use."
}

run_as_daemon=0
nopm=0
init_db=1
dbname=''
dbport=''

function checkOption {
  for option in "$@"
  do
    echo process option $option
    if [[ $option == "nopm" ]]
    then
      nopm=1
    elif [[ $option == "nopmd" ]]
    then
      nopm=1
      run_as_daemon=1
    elif [[ $(echo $option | grep -E "^dbn=") != "" ]]
    then
      dbname=${option:4}
    elif [[ $(echo $option | grep -E "^dbp") != "" ]]
    then
      dbport=${option:4}
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
./initmogodb.sh ii=../../data/initial_db_data/imagemeta.json ht=127.0.0.1 pt=27017 db=sotares
cd ..
fi


if [ $nopm -eq 1 ]
then
  if [ $run_as_daemon -eq 1 ]
  then
    nohup npm start dbn=$dbname dbp=$dbport&
  else
    npm start dbn=$dbname dbp=$dbport
  fi
else
  service start 
  if [ $? -ne 0 ]
  then
    echo fail to start sota server!!!!
    echo to run sota server with  pm, you must have admin priviledge!!
  fi
fi
