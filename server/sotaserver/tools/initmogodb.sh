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

function showUsage {
  echo "usage: " $(echo $0 | grep -E -o '[^\/]+$') "ii=file_name ht=db_host pt=db_port db=dbname"
  echo "  detail : ii=file_name file contains image info data in JSON"
  echo "           ht=db_host  DB host"
  echo "           pt=db_port DB port"
  echo "           db=dbname specify the db name to use. Must be one of mongo or mockup"
}

ii=
ht=
pt=
dn=

function checkPort {
  local port=$(echo $1 | grep -E "^[0-9]+"$)
  if [[ $1 != $port ]]
  then
    echo Invalid port number
    showUsage
    exit
  fi
  return
}

function checkOption {
  for option in "$@"
  do
    local iio=$(echo $option | grep -E "^ii=")
    local dbo=$(echo $option | grep -E "^db=")
    local hto=$(echo $option | grep -E "^ht=")
    local pto=$(echo $option | grep -E "^pt=")

    if [[ $iio != "" ]]
    then
      ii=${iio:3}
    elif [[ $pto != "" ]]
    then 
      pt=${pto:3}
      checkPort $websocket_port
    elif [[ $dbo != "" ]]
    then
      dn=${dbo:3}
    elif [[ $hto != "" ]]
    then
      ht=${hto:3}
    else
      echo invalid option
      showUsage
      exit
    fi
  done
  echo 
}

if [ $# -eq 4 ]
then
  checkOption $@
else
  echo $#
  showUsage
  exit
fi
 
node initMongoDB.js dbname=$dn host=$ht port=$pt imageinfo=$ii
