#!/usr/bin/env python
# coding: utf8

# This renders the template files from 'src' into 'www'

import os
import sys
from os.path import join, normpath, exists, islink
import datetime
from shutil import copy2
import jinja2 as j2

# go to where the script is to get relative paths right
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# we operate in "src"
os.chdir("./src")
j2env = j2.Environment(loader=j2.FileSystemLoader("."))

TARG = "../www"

IGNORE_PATHS = ["old"]


def log(what, level=0, nl=True):
    from sys import stdout
    if level == 0:
        return
    elif level == 1:
        stdout.write(what)
    if nl:
        stdout.write('\n')
    stdout.flush()

for root, paths, filenames in os.walk("."):
    # check if we ignore a branch in a sub-tree
    root_split = root.split(os.sep)
    if len(root_split) > 1 and root_split[1] in IGNORE_PATHS:
        continue

    # path need to exist in the target before we copy and process the files
    for path in paths:
        target_path = normpath(join(TARG, root, path))
        log("path %s -> %s" % (path, target_path))
        if not exists(target_path):
            os.makedirs(target_path)

        # we also have to take care of symlinks here!
        if islink(join(root, path)):
            log("SYMLINK/paths: %s" % join(root, path))

    for fn in filenames:
        src = join(root, fn)
        dst = normpath(join(TARG, root, fn))

        log("processing %s in %s ..." % (fn, root))
        log('.', level=1, nl=False)

        if fn.endswith(".html"):
            # assume it's a template and process it
            tmpl = j2env.get_template(src)
            content = tmpl.render()
            with open(dst, "wb") as output:
                output.write(content.encode("utf-8"))
                output.write(b"\n")

        elif islink(src):
            # we have a symlink, copy it
            log("SYMLINK/files %s" % src)
            if islink(dst):
                os.remove(dst)
            linkto = os.readlink(src)
            os.symlink(linkto, dst)

        else:
            # all other files, copy them
            copy2(src, dst)

log('\nFinished', level=1)
