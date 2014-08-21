#!/usr/bin/env python
# -*- coding: utf8 -*-
# this script moves all the the SPKG.txt descriptions to the
# spkg/upstream/*/ directories.

import os
import cgi
from glob import glob
#import codecs

NOTES_TMPL_1 = """
<div>
<style>
pre#spkg {
  max-height: 23em;
  overflow-y: auto;
  white-space: pre-wrap;
}
</style>
<pre id="spkg">
"""
NOTES_TMPL_2 = "</pre></div>"

# step 1: update the ~/sage-git directory
os.chdir(os.path.expanduser("~/sage-git"))
os.system("git fetch origin")
os.system("git checkout develop")
os.system("git reset --hard origin/develop")

# step 2: construct path to source SPPK and
# walk through all the directories in the target directories
src_dir = os.path.expanduser("~/sage-git/build/pkgs/")
targ_dir = os.path.expanduser("~/www-files/spkg/upstream/")
os.chdir(targ_dir)
print "starting"
for dirname in glob("*"):
    if not os.path.isdir(dirname):
        continue
    # check if index.html exists (if not, also create md5sums.txt)
    if not os.path.exists(os.path.join(dirname, "index.html")):
        for auxfn in ["index.html", "md5sums.txt"]:
            os.system("touch %s" % os.path.join(dirname, auxfn))
    spkg_txt = os.path.join(src_dir, dirname, "SPKG.txt")
    if not os.path.exists(spkg_txt):
        print "WARNING: %s does not exist" % spkg_txt
        continue
    spkg_target = os.path.join(targ_dir, dirname, "notes.txt")
    print "%-25s" % dirname,
    # print spkg_txt,
    txt = open(spkg_txt, "rb").read()  # .decode("utf8")
    f = open(spkg_target, "wb")
    try:
        f.write(NOTES_TMPL_1)
        f.write(cgi.escape(txt))
        f.write(NOTES_TMPL_2)
    finally:
        f.close()
    print "ok"
