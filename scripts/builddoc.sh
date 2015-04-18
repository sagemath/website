#!/usr/bin/env bash

###########################################################################
# Copyright (c) 2010 Minh Van Nguyen <nguyenminh2@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# http://www.gnu.org/licenses/
###########################################################################

# Wrap up the HTML and PDF versions of the standard Sage documentation.


##############################
# environment variables
##############################

SAGE_ROOT=$(readlink -e "$1")
SAGE_DOC=$SAGE_ROOT/src/doc
SAGE_DOC_PDF=$SAGE_DOC/output/pdf
SAGE_VERSION="$2"


##############################
# helper functions
##############################

# Put PDF version of documentation in one top level directory.
#
# INPUT:
#
# - dir -- a directory containing PDF files
#
# OUTPUT:
#
# - Move all PDF documents in subdirectories of dir to the top level directory
#   dir. The subdirectories are then removed once all their PDF files have
#   been relocated to dir.
function relocate_pdf {
    cd $SAGE_DOC_PDF/$1
    for dir in `/bin/ls`; do
	if [ -d $dir ]; then
	    for file in `find $dir`; do
		echo $file | grep --quiet '\.pdf$'
		if [ $? -eq 0 ]; then
		    mv $file $SAGE_DOC_PDF/$1
		fi
	    done
	    rm -rf $dir
	fi
    done
    cd $SAGE_ROOT
}


##############################
# script body
##############################

# rebuild Sage library
cd $SAGE_ROOT
#./sage -b master

# (re)generate documentation
rm -rf src/doc/output/
if [ -f dochtml.log ]; then
    rm dochtml.log
fi
./sage -docbuild --no-pdf-links all html 2>&1 | tee -a dochtml.log
if [ -f docpdf.log ]; then
    rm docpdf.log
fi
./sage -docbuild all pdf 2>&1 | tee -a docpdf.log

# relocate_pdf en
# relocate_pdf fr
cd $SAGE_ROOT
cp -rlf $SAGE_DOC/output sage-"$SAGE_VERSION"-doc
rm -rf sage-"$SAGE_VERSION"-doc/doctrees
rm -rf sage-"$SAGE_VERSION"-doc/latex
tar -jcf sage-"$SAGE_VERSION"-doc.tar.bz2 sage-"$SAGE_VERSION"-doc
rm -rf sage-"$SAGE_VERSION"-doc

exit 0
