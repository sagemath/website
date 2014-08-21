#!/usr/bin/env python

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

# README
#
# The purpose of this script is to centralize the updating of the Sage website
# for each new Sage release. Currently this goal is far from being realized,
# as many of the tasks involved in updating the Sage website for each release
# are still done by hand.
#
# To use this script, run it as follows
#
# $ ./export.py /path/to/SAGE_ROOT/
#
# where /path/to/SAGE_ROOT/ is the absolute or relative path to the SAGE_ROOT
# of a pre-compiled version of Sage. Then the script would perform the
# following tasks:
#
# * Generate the documentation for the version of Sage as contained under
#   /path/to/SAGE_ROOT/.
#
# * Update the website with the newly generated documentation.
#
# * Push all changes to the Mercurial repository at hg.sagemath.org.

import os
from subprocess import Popen
import sys

##############################
# helper functions
##############################


def usage():
    """
    Print the usage information for this script.
    """
    print "".join(["Usage: ", sys.argv[0], " /path/to/SAGE_ROOT/"])
    sys.stdout.flush()

##############################
# the script starts here
##############################

PWD = os.getcwd()

# sanity checks
if len(sys.argv) != 2:
    usage()
    sys.exit(1)
SAGE_ROOT = os.path.abspath(sys.argv[1])
if not os.path.isdir(SAGE_ROOT):
    print("Invalid SAGE_ROOT %s. Exiting..." % SAGE_ROOT)
    sys.stdout.flush()
    sys.exit(1)
SAGE_SAGE = os.path.join(SAGE_ROOT, "sage")
if not os.path.isfile(SAGE_SAGE):
    print("Invalid Sage start up script %s. Exiting..." % SAGE_SAGE)
    sys.stdout.flush()
    sys.exit(1)

# generate and update documentation
DOC_SCRIPT = "updatedoc.py"
if not os.path.isfile(DOC_SCRIPT):
    print("Documentation update script %s not found. Exiting..." % DOC_SCRIPT)
    sys.stdout.flush()
    sys.exit(1)
sh = Popen("./%s %s" % (DOC_SCRIPT, SAGE_ROOT), shell=True)
sh.communicate()
if sh.returncode != 0:
    print("Error updating documentation. Exiting...")
    sys.stdout.flush()
    sys.exit(1)

# push changes to Mercurial repository hg.sagemath.org
# HG_SCRIPT = "/home/sagemath/bin/sage-pushall"
# if not os.path.isfile(HG_SCRIPT):
#     print("Mercurial repository update script %s not found. Exiting..." % HG_SCRIPT)
#     sys.stdout.flush()
#     sys.exit(1)
# os.chdir("%s" % SAGE_ROOT)
# sh = Popen("%s" % HG_SCRIPT, shell=True)
# sh.communicate()
# if sh.returncode != 0:
#     print("Error updating Mercurial repository hg.sagemath.org. Exiting...")
#     sys.stdout.flush()
#     sys.exit(1)
# os.chdir(PWD)

# push to the mirrors
# MIRROR_SCRIPT = "/home/sagemath/mirror"
# if not os.path.isfile(MIRROR_SCRIPT):
#     print("Mirror script %s not found. Exiting..." % MIRROR_SCRIPT)
#     sys.stdout.flush()
#     sys.exit(1)
# os.system(MIRROR_SCRIPT)
