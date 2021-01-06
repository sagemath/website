#!/usr/bin/env python
"""
This script goes through all package directories.
It links to them together with a description on the website.
There is also a list file listing them.
Archive is the directory of outdated files, which are moved there.

Rewritten based on an old generator file by Harald Schilly, 2008.
"""

from os.path import join, makedirs, exists
import os
import sys
from glob import glob
from xml.dom.minidom import parse

# script uses relative paths, switch to its
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# this is the target html file, where to write to
out_html = join('.', 'www', 'download-packages2.html')
doc = parse(out_html)
end_spkg = '*.spkg'
end_desc = '*.txt'

package_dir = join('.', 'www', 'packages')

# this dict associates html-id-tags with directories where to index
packages = {
    'standard': join(package_dir, 'standard'),
    'optional': join(package_dir, 'optional'),
    'experimental': join(package_dir, 'experimental'),
    'archive': join(package_dir, 'archive')
}


def package_name(F):
    """
    copied over from the original gen_html and modified
    """
    return F.split('-')[0]


def archive_all_but_newest(F, D):
    """
    copied over from the original gen_html
    """
    if not exists(F):
        return
    if not exists(packages['archive']):
        print('mkdir: %s' % makedirs(packages['archive']))
    name = package_name(F)
    versions = sorted([(os.path.getmtime(m), m) for m in D if os.path.exists(m) and package_name(m) == name])
    for G in versions[:-1]:
        print("Archiving %s..." % G[1])
        cmd = "mv %s.* %s" % (G[1][:-5], packages['archive'])
        print(cmd)
        # system(cmd)


for P, DIR in packages.items():

    print('P:%s - DIR:%s' % (P, DIR))
    FILES = glob(join(DIR, end_spkg))
    for F in FILES:
        print('F', F)
        if DIR != packages['archive']:
            archive_all_but_newest(F, FILES)
        DESC = F.replace(end_spkg[1:], end_desc[1:])
        if exists(DESC):
            print('DESC:', DESC)
            O = open(DESC).read()
            i = O.find('\n')
            if i != -1:
                DESC_txt = O[:i]
                DESC_det = O[i + 1:]
            else:
                DESC_txt = O
                DESC_det = ""
            print('DESC_txt =', DESC_txt)
            print('DESC_det =', DESC_det)
