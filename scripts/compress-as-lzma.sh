#!/usr/bin/env bash

# this script trans-compresses a tar.* file into tar.lzma
# because lzma performs significantly better and is part of
# the tar-tools in linux


if [ -z $1 ]; then
  echo this script converts tar.gz or tar.bzip2 binary distributions with lzma
  echo Usage: $0 input_file.tar.gz
  exit 0
fi

if [ ! -s $1 ]; then
  echo file $1 must exists and length ">" 0
  exit 0
fi

# tests
export LANG=C

if [[ $(file $1 | grep bzip2 | wc -l) == 1 ]]; then
  echo bzip2 dedected
  DECOMP="bzcat"
  LZMA=${1/%bzip2/}lzma
elif [[ $(file $1 | grep gzip| wc -l) == 1 ]]; then
  echo gzip dedected
  DECOMP="zcat"
  LZMA=${1/%gz/}lzma
else
  echo "it\'s neither a bzip2 or gzip file :("
fi


IN=$1
OUT=`basename $LZMA`

CMD="$DECOMP $IN | nice lzma -zv > $OUT"

#read -p "Run $CMD [y/N]?"
#
#if [[ $REPLY == "y" ]]; then
# eval $CMD
#else
# echo aborted
# exit 0
#fi

eval $CMD

if [ $? -ne 0 ]; then
    echo Error Compressing File $IN
    exit 1
fi


#echo "deleting original file"
#rm $IN
