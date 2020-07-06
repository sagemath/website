#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from glob import glob

if len(sys.argv) == 1:
    raise Exception("First argument needs to be the source path of the *tar.gz files")

if not os.popen("whoami").read().startswith("sagemath"):
    raise Exception("You need to be 'sagemath' to run this script. sudo -H -u sagemath ./mirror_upstream ...")

SRC_DIR = os.path.abspath(sys.argv[1])
TARG_DIR = "/home/sagemath/www-files/spkg/upstream"

for ext in ["*.tar.gz", "*.tar.bz2", "*.tar"]:
    for f in glob(os.path.join(SRC_DIR, ext)):
        fn = os.path.basename(f)
        subdir = fn.split("-")[0].lower()
        targ_fn = os.path.join(TARG_DIR, subdir, fn)
        if os.path.exists(targ_fn):
            if os.stat(targ_fn).st_ctime >= os.stat(f).st_ctime:
                print("WARNING %s already exists" % targ_fn)
                continue
        os.system("cp -av %s %s" % (f, targ_fn))
