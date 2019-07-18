#!/bin/bash

echo Warning: This script must be invoked by administrator who has root priviledge.
# option check

function showUsage {
  echo "usage: " $(echo $0 | grep -E -o '[^\/]+$') "dst=install_directory [option]"
  echo "  option : src=source_of_install"
}

dst=""

for option in "$@"
do
  echo process option $option
  if [[ $option == "src" ]]
  then
    echo option src is not supported yet.
  elif [[ $(echo $option | grep -E "^dst=") != "" ]]
  then
    dst=${option:4}
  else
    showUsage
    exit
  fi
done

if [[ "$dst" == "" ]]
then
    showUsage  
    exit
fi

if [ ! -d $dst ]
then
    if [ -e $dst ]
    then
      echo Invalid destination
      exit
    fi

    echo Create destination diretory: $dst
    mkdir -p $dst
    if [ $? -ne 0 ]
    then
      echo fail to create $dst
      exit
    fi
fi

echo 

# First, make user and group
# mongodb -> dbadmin / sota 
# server -> sota / sota
# certificate -> certiadmin / sota
# image -> uploader / sota

sotaserver="sotaserver"
certiadmin="certiadmin"
dbadmin="dbadmin"
uploader="uploader"
sotausers="$dbadmin $sotaserver $certiadmin $uploader"
loginuser="uploader"
sotagroup="sotagroup"

eusers=$(cut -d: -f1 /etc/passwd)
egroups=$(cut -d: -f1 /etc/group)

exist=0

for group in $egroups
do
  if [[ "$group" == "$sotagroup" ]]
  then
    exist=1
    break;
  fi
done

if [ $exist -eq 0 ]
then
  echo create group : $sotagroup
  addgroup --disabled-login $sotagroup
  if [ $? -ne 0 ]
  then
    echo Fail to create $sotagroup 
  fi
fi

for sotauser in $sotausers
do
  exist=0
  for eusers in $eusers 
  do
    if [[ "$eusers" == "$sotauser" ]]
    then
      exist=1
      break
    fi
  done 
  
  if [ $exist -eq 0 ]
  then
    echo create user $sotauser
    if [[ "$sotauser" == "$loginuser" ]]
    then
      adduser --no-create-home --ingroup $sotagroup $sotauser
    else
      adduser --no-create-home --disabled-login --ingroup $sotagroup $sotauser
    fi
    adduser $sotauser $sotagroup
    adduser $sotauser users
  else
    users_in_sota=$(cat /etc/group | grep sotagroup | cut -d: -f4)
    exist=0
    echo users in sota: $users_in_sota
    for guser in $users_in_sota
    do
      if [[ "$guser" == "$sotauser" ]]
      then
        exist=1
        break
      fi
    done
    if [ $exist -eq 0 ]
    then
      echo Add $sotauser to $sotagroup
      adduser $sotauser $sotagroup
    fi
  fi
done

echo "User/group for SOTA ==> DONE"

echo 
echo copy source


if [ "$(echo $0 | grep -E -o '^\./')" == "./" ]
then
  absolute_path=$PWD/$(echo $0 | sed -E '{s/[^\/]+$//}' | sed -E '{s/^\.\///}')
else
  absolute_path=$(echo $0 | sed -E '{s/[^\/]+$//}')
fi

SRC_ROOT=$absolute_path..
nodedir="node-v12.6.0-linux-x64"
mongoddir="mongodb-linux-x86_64-ubuntu1804-4.0.10"
sotadir=sotaserver
dir_to_copy="$nodedir $mongoddir $sotadir"
rmdir_after_copy="sotaserver/tools sotaserver/test"

for dir in $dir_to_copy
do
  cp -r $SRC_ROOT/$dir $dst/
done

for dir in $rmdir_after_copy
do
  rm -rf $dst/$dir
done

# set owner of sota application
chown -R $sotaserver:$sotagroup $dst
chmod -R 550 $dst

# set up certificate
mkdir -p $dst/certificate
cp $SRC_ROOT/installer/cert/* $dst/certificate/
chown -R $certiadmin:$sotagroup $dst/certificate
chmod -R 740 $dst/certificate

# prepare service directory
mkdir -p $dst/service
mkdir -p $dst/run

# set up db directory
mkdir -p $dst/db/data
mkdir -p $dst/db/log

mkdir -p $absolute_path/temp
echo s#MONGOD_CONF_PATH#$dst/service# > $absolute_path/temp/mongod.sed
echo s#MONGOD_BIN_PATH#$dst/$mongoddir/bin# >> $absolute_path/temp/mongod.sed
echo s#RUN_PATH#$dst/run# >> $absolute_path/temp/mongod.sed

sed -f $absolute_path/temp/mongod.sed $absolute_path/service/mongod > $dst/service/mongod
ln -s $dst/service/mongod /lib/systemd/system/mongod.service
 
echo s#MONGOD_DB_ROOT_PATH#$dst/db# > $absolute_path/temp/mongod.sed
echo s#RUN_PATH#$dst/run# >> $absolute_path/temp/mongod.sed

sed -f $absolute_path/temp/mongod.sed $absolute_path/service/mongod.conf > $dst/service/mongod.conf

chown -R $dbadmin:$sotagroup $dst/$mongoddir 
chmod -R 700 $dst/$mongoddir

chown -R $dbadmin:$sotagroup $dst/db
chmod -R 700 $dst/db

# set up image directory
mkdir -p $dst/image
cp $SRC_ROOT/installer/image/* $dst/image/
chown -R $uploader:$sotagroup $dst/image
chmod -R 740 $dst/image

echo copy done

echo 
echo set-up server service
echo s#NODE_BIN_PATH#$dst/$nodedir/bin# > $absolute_path/temp/server.sed
echo s#SOTA_SERVER_BIN_PATH#$dst/$sotadir/bin# >> $absolute_path/temp/server.sed
echo s#RUN_PATH#$dst/run# >> $absolute_path/temp/server.sed

sed -f $absolute_path/temp/server.sed $absolute_path/service/sotaserver > $dst/service/sotaserver
ln -s $dst/service/sotaserver /lib/systemd/system/sotaserver.service
 
chown -R $sotaserver:$sotagroup $dst/service
chown $dbadmin:$sotagroup $dst/service/mongod.conf
chown $dbadmin:$sotagroup $dst/service/mongod
chmod -R 550 $dst/service

chown -R $stoaserver:$sotagroup $dst/run
chmod -R 770 $dst/run

rm -rf $absolute_path/installer/temp

echo 

# start service
echo enable service
systemctl daemon-reload
ln -s /lib/systemd/system/mongod.service /etc/systemd/system/mongd.service
ln -s /lib/systemd/system/sotaserver.service /etc/systemd/system/sotaserver.service
systemctl start mongod
systemctl start sotaserver

# initialization DB

sed -E "{s#ROOT_PATH#$dst#}" $absolute_path/db/imagemeta.json > $absolute_path/temp/imagemeta.json

cd $absolute_path/../sotaserver/tools

backuppath=$PATH
export PATH=$absolute_path../$nodedir/bin:$PATH
./initmogodb.sh ii=$absolute_path/temp/imagemeta.json ht=127.0.0.1 pt=30718 db=sotares
export PATH=$backuppath
cd -

echo "All done. Now you can invoke start_server.sh to run sota server!!"

