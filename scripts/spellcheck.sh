#!/bin/bash

if [ -z $1 ]; then 
	echo "usage: $0 file.html ... checks webpage file.html in language en_US as webpage using aspell"
	exit 0
fi

aspell -H -l en_US -c $1
