#!/bin/bash

if [ $# -ne 1 ]
then
  echo no installation path
  exit
fi

if [ "$(echo $0 | grep -E -o '^\./')" == "./" ]
then
  absolute_path=$PWD/$(echo $0 | sed -E '{s/[^\/]+$//}' | sed -E '{s/^\.\///}')
else
  absolute_path=$(echo $0 | sed -E '{s/[^\/]+$//}')
fi

mkdir -p $absolute_path/temp


index=0

while [[ "1" == "1" ]]
do

  imagemeta=db/imagemeta$index.json
  cd $absolute_path/../sotaserver/tools

  echo Update db from $imagemeta
  sed -E "{s#ROOT_PATH#$1#}" $absolute_path/$imagemeta > $absolute_path/temp/imagemeta.json

  backuppath=$PATH
  export PATH=$absolute_path../$nodedir/bin:$PATH
  ./initmogodb.sh ii=$absolute_path/temp/imagemeta.json ht=127.0.0.1 pt=30718 db=sotares
  export PATH=$backuppath
  index=$((index + 1))


  sleep 10


  echo $index
  if [ $index -gt 2 ]
  then 
    index=0
    ./initmogodb.sh ii='init' ht=127.0.0.1 pt=30718 db=sotares
  fi

  cd -

done

rm -rf $absolute_path/temp

