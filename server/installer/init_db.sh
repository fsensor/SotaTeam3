#!/bin/bash

if [ "$(echo $0 | grep -E -o '^\./')" == "./" ]
then
  absolute_path=$PWD/$(echo $0 | sed -E '{s/[^\/]+$//}' | sed -E '{s/^\.\///}')
else
  absolute_path=$(echo $0 | sed -E '{s/[^\/]+$//}')
fi

mkdir -p $absolute_path/temp

cd $absolute_path/../sotaserver/tools

backuppath=$PATH
export PATH=$absolute_path../$nodedir/bin:$PATH
./initmogodb.sh ii='init' ht=127.0.0.1 pt=30718 db=sotares
export PATH=$backuppath


cd -

rm -rf $absolute_path/temp

