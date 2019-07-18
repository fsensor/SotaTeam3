#!/bin/bash

if [ $# -ne 2 ]
then
  echo "usage: " $(echo $0 | grep -E -o '[^\/]+$') "install_path" "db_data"  
  exit
fi

if [ "$(echo $0 | grep -E -o '^\./')" == "./" ]
then
  absolute_path=$PWD/$(echo $0 | sed -E '{s/[^\/]+$//}' | sed -E '{s/^\.\///}')
else
  absolute_path=$(echo $0 | sed -E '{s/[^\/]+$//}')
fi

mkdir -p $absolute_path/temp

cd $absolute_path/../sotaserver/tools

echo Update db from $2
sed -E "{s#ROOT_PATH#$1#}" $absolute_path/$2 > $absolute_path/temp/imagemeta.json

backuppath=$PATH
export PATH=$absolute_path../$nodedir/bin:$PATH
./initmogodb.sh ii=$absolute_path/temp/imagemeta.json ht=127.0.0.1 pt=30718 db=sotares
export PATH=$backuppath


cd -

rm -rf $absolute_path/temp

