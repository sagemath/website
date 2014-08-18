#!/usr/bin/env bash
cd 
cd www2-dev/www
cp -av ~/../mvngu/apps/pubparse/*.bib files/
cp -av ~/../mvngu/apps/pubparse/*.html .
../go_live.sh
