#!/usr/bin/env python
# coding: utf8

# This renders the template files from 'src' into 'www'

import os, sys
import datetime
import shutil
import jinja2 as j2

# go to where the script is to get relative paths right
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# we operate in "src"
os.chdir("./src")
j2env = j2.Environment(loader=j2.FileSystemLoader("."))

TARG="../www"

for root, path, filenames in os.walk("."):
    for fn in filenames:
        if not fn.endswith(".html"): continue
        if "template" in root: continue
        print "processing %s in %s ..." % (fn, root)

        src = os.path.join(root, fn)
        dst = os.path.normpath(os.path.join(TARG, root, fn))
        tmpl = j2env.get_template(src)
        content = tmpl.render()
        with open(dst, "wb") as output:
            output.write(content.encode("utf-8"))
            output.write(b"\n")



