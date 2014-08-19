#!/usr/bin/env python
# coding: utf8

# This renders the template files from 'src' into 'www'

import os
import sys
from os.path import join, normpath, exists, islink
import datetime
from shutil import copy2
import yaml
import jinja2 as j2

# go to where the script is to get relative paths right
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

config = yaml.load(open('config.yaml'))

# we operate in "src"
os.chdir("./src")
j2env = j2.Environment(loader=j2.ChoiceLoader(
    [j2.FileSystemLoader("."), j2.FileSystemLoader("../publications/")]))
j2env.globals.update(config)

TARG = "../www"

IGNORE_PATHS = ["old"]


def log(what, nl=True):
    from sys import stdout
    write = stdout.write
    if len(what) > 100:
        what = '%s…' % what[:99]
    what = '{:100}'.format(what)
    if not nl:
        write('\r')
    elif not log.lastnl:
        write('\n')
    stdout.write(what)
    if nl:
        write('\n')
    stdout.flush()
    log.lastnl = nl
log.lastnl = True

log("config:")
for line in yaml.dump(config, indent=True, default_flow_style=False).splitlines():
    log("    %s" % line)

for root, paths, filenames in os.walk("."):
    # check if we ignore a branch in a sub-tree
    root_split = root.split(os.sep)
    if len(root_split) > 1 and root_split[1] in IGNORE_PATHS:
        continue

    # path need to exist in the target before we copy and process the files
    for path in paths:
        src = join(root, path)
        dst = normpath(join(TARG, src))

        log("processing/d: %s" % src, nl=False)

        # we have to take care of symlinks here, too!
        if islink(src):
            #log("SYMLINK/paths: %s" % src)
            os.symlink(os.readlink(src), dst)

        elif not exists(dst):
            os.makedirs(dst)

    for fn in filenames:
        src = join(root, fn)
        dst = normpath(join(TARG, src))

        log("processing/f: %s" % src, nl=False)

        if fn.endswith(".html"):
            # assume it's a template and process it
            tmpl = j2env.get_template(src)
            content = tmpl.render()
            with open(dst, "wb") as output:
                output.write(content.encode("utf-8"))
                output.write(b"\n")

        elif islink(src):
            # we have a symlink, copy it
            #log("SYMLINK/files %s" % src)
            if islink(dst):
                os.remove(dst)
            os.symlink(os.readlink(src), dst)

        else:
            # all other files, copy them
            copy2(src, dst)

log("processing: done", nl=False)

log('Finished')
