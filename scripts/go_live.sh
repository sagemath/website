#!/bin/bash
# This script uploads content changes to avoid broken files in between
# source: a directory where you edit, public subpage "sagemath.org/sandbox" just for you and blacklisted in robots.txt
# target: a directory, which is the actual page: www.sagemath.org

echo "NOT THIS go_live.sh, the one from the dir above!"
exit 1

# this makes sure, that the relative paths are relative to the script location!
base=`dirname "$0"`
cd $base

# the actual publishing
source="./www/"
# WARNING: if you modify $target, you also have to modify the path in ./timestamp.py AND ./mirror_master.py !!!!
target="/home/sagemath/www2/"

rsync -av --delete $source $target
#sudo -u sagemath rsync -av --delete $source $target

