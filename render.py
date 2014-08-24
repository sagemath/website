#!/usr/bin/env python
# coding: utf8
#
# This renders the template files from 'src' into 'www'
#
# Author: Harald Schilly <harald@schil.ly>
# License: Apache 2.0

import os
import sys
from os.path import join, normpath, exists, islink
import datetime
import shutil
import yaml
import jinja2 as j2

from scripts import log
from conf import config, mirrors, packages

# go to where the script is to get relative paths right
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

if not exists("www"):
    os.mkdir("www")

log("config:")
for line in yaml.dump(config, indent=True, default_flow_style=False).splitlines():
    log("    %s" % line)
log("    %d mirrors" % len(mirrors))

# everything is now rooted in the src directory
os.chdir("src")

tmpl_dirs = [join("..", _) for _ in ["publications", "templates", "src"]]
j2loader = j2.FileSystemLoader(tmpl_dirs)
j2env = j2.Environment(loader=j2loader)
j2env.globals.update(config)


@j2.contextfilter
def filter_prefix(ctx, link):
    """
    Prepend level-times "../" to the given string.
    Used to go up in the directory hierarchy.
    Yes, one could also do absolute paths, but then it is harder to debug locally!
    """

    level = ctx.get("level", 0)
    if level == 0:
        return link
    path = ['..'] * level
    path.append(link)
    return '/'.join(path)

j2env.filters["prefix"] = filter_prefix

TARG = join("..", "www")  # assumption: completely empty www

IGNORE_PATHS = ["old"]

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
            #log("mkdir %s" % dst)
            os.makedirs(dst)

    for fn in filenames:
        src = join(root, fn)
        dst = normpath(join(TARG, src))
        lvl = root.count(os.sep)

        log("processing/f: %s" % src, nl=False)

        if fn.endswith(".html"):
            # we ignore html files starting with "_" (e.g. language templates)
            if fn.startswith("_"):
                continue
            # assume it's a template and process it
            tmpl = j2env.get_template(src)
            c = fn.rsplit(".", 1)[0].split("-", 1)[0]
            content = tmpl.render(level=lvl, filename=fn, category=c)
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
            # all other files, hardlink them
            #log("hardlink %s -> %s" % (src, dst))
            os.link(src, dst)

log("processing: done", nl=False)

log('Finished')
