#!/bin/bash

# Find path to this script

if [ "$(echo $0 | grep -E -o '^\./')" == "./" ]
then
  absolute_path=$PWD/$(echo $0 | sed -E '{s/[^\/]+$//}' | sed -E '{s/^\.\///}')
else
  absolute_path=$(echo $0 | sed -E '{s/[^\/]+$//}')
fi


function showUsage {
  echo "usage: " $(echo $0 | grep -E -o '[^\/]+$') "[option]"
  echo "  option : d   run as daemon"
}

cd $absolute_path

DB_PATH=mongodb-linux-x86_64-ubuntu1804-4.0.10/bin
DB_DATA_DIR=./db/data
DB_LOG_DIR=./db/log
DB_LOG_FILE=sotaserverdb.log

export PATH=$absolute_path$DB_PATH:$PATH

if [ ! -d $DB_DATA_DIR ]
then
  echo "Create DB data dir"
  mkdir -p $DB_DATA_DIR
fi

if [ ! -d $DB_LOG_DIR ]
then
  echo "Create DB LOG dir"
  mkdir -p $DB_LOG_DIR
fi

function errorhandle {
  if [ $1 -ne 0 ] 
  then 
    echo $2
    echo "Please check you run this script with root priviledge!"
    exit
  fi
}

echo "Run mongodb daemon"
mongod --dbpath $DB_DATA_DIR --logpath $DB_DATA_DIR/$DB_LOG_FILE --fork

errorhandle $? "Fail to run mongodb daemon"

SLP_SERVICE_NAME=sotaslpm
SLP_SERVICE_FILE=$SLP_SERVICE_NAME.service
REAL_SLP_SERVICE_FILE=strong-pm.service
SLP_SERVICE_SED_FILE=$REAL_SLP_SERVICE_FILE.sed
SLP_DIR=strong-pm
SLP_PATH=$absolute_path$SLP_DIR
ESCAPED_SLP_PATH=$(echo $SLP | sed -E "")
SYSTEMD_FILE_PATH=/lib/systemd/system/

TO_BE_REPLACED=REPLACE_TO_REAL_PATH

# Replace environment
if [ ! -f $SLP_PATH/systemd/$REAL_SLP_SERVICE_FILE ]
then
  echo "Generating StrongLoop PM service file"
  sed -E "s#$TO_BE_REPLACED#$SLP_PATH/pm#" $SLP_PATH/systemd/$SLP_SERVICE_SED_FILE > $SLP_PATH/systemd/$REAL_SLP_SERVICE_FILE
fi


# First remove service file in default path
echo "Update link"
rm -f $SYSTEMD_FILE_PATH$SLP_SERVICE_FILE
ln -s $SLP_PATH/systemd/$REAL_SLP_SERVICE_FILE $SYSTEMD_FILE_PATH$SLP_SERVICE_FILE


echo "Run StrongLoop PM"
service strong-pm start
errorhandle $? "Fail to run mongodb daemon"

echo "All done. Now you can invoke start_server.sh to run sota server!!"
