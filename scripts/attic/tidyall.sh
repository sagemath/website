#!/bin/bash
# This script simply searches for all html files and runs tidy with
# the suitable options file on them 



pushd `dirname "$0"`
BASE=`pwd`
optfile=$BASE"/options_tidy.txt"
echo $optfile
popd

echo "TIDY IS EVIL... never works with SSI and in the end more troubles than benefits ... maybe it is fixed some time in the future ... therefore only use for those files where no SSI variables are called inside quotes (i.e. in href=)!"

#if [ -z $1 ]; then
#        optfile="options_tidy.txt"
#else
#        optfile=$1
#fi
#
#find . -wholename "./www/inc" -prune -o -type f -iname "*.html" -exec echo {} \; -exec tidy -q -m -config $optfile {} \;


if [ -z $1 ] ; then
	echo "Usage: $0 <file>"
	exit
fi
tidy -q -m -config $optfile $1

