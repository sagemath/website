#!/usr/bin/env python
# no python 2.6, see below for workaround!
"""
This script prints a timestamp into the timestamp.html file for the mirrors
 * the current gmt time
 * version number (release / source) from variables.shtml
 * a hashcode of all filenames of files >10MB and their mtimes
copyright: Harald Schilly <harald.schilly@gmail.com>, 2008, Vienna, Austria
license: gpl v2+
"""
import os
import sys
import time
import re
from hashlib import md5

# script uses relative paths, switch to its
# os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
# NO, IT DOES NOT
os.chdir(os.path.expanduser("~"))

#if len(sys.argv) != 2:
#  raise Exception("first argument must be the root directory of the files to mirror! e.g. ~/files")
#ROOT = os.path.abspath(os.path.expanduser(sys.argv[1]))
#os.chdir(ROOT)


SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

def getMirrorHash():
    # python 2.6 version, nicer, but needs followlinks !!!
    #hash = md5.new()
    # for r, d, files in os.walk(os.path.join('.', 'www', 'mirror'), followlinks=True):
    #   for f in files:
    #      st = os.stat(os.path.join(r, f))
    #      if st.st_size < 10**6:
    #         continue
    #      m = st.st_mtime
    #      print os.path.join(r, f)
    #      hash.update(str(m))
    #      hash.update(f)
    # return hash.hexdigest()
    # workaround:
    import subprocess
    s = subprocess.Popen('find -L files/ -type f -and '
                         '\( -size +10M -not -path "*src*" -not -path "*devel*" -not -path "*meta*" -not -name "*.spkg" \) '
                         '-exec ls -la {} \; | md5sum | cut -d" " -f1',
                         shell=True, stdout=subprocess.PIPE)
    return s.stdout.readline().split('\n')[0]


def getSpkgHash():
    import subprocess
    s = subprocess.Popen('find -L files/ -type f -and '
                         '\(  \( -path "*src*" -and -size +100M \)  '
                         '-or \( -path "*standard*" -and -name "*.spkg" -or -name "*install" \) \) '
                         '-exec ls -la {} \; | md5sum | cut -d" " -f1',
                         shell=True,
                         stdout=subprocess.PIPE)
    return s.stdout.readline().split('\n')[0]


def getVersion():
    """extracts version number"""
    import yaml
    conf = yaml.load(open(os.path.join("website", "conf", "config.yaml")))
    ver = conf["version"]
    src = conf["version_src"]
    #for l in open(os.path.join('website', 'www', 'inc', 'variables.shtml')):
    #    m = re.search(r'var="version"\s+value="(.*)"', l)
    #    if not m is None and len(m.groups()) >= 1:
    #        ver = m.group(1)
    #    m = re.search(r'var="version-src"\s+value="(.*)"', l)
    #    if not m is None and len(m.groups()) >= 1:
    #        src = m.group(1)
    return str(ver), str(src)


def writeMirrorTimestamp(msg, STAMP):

    stampstring = time.strftime('%Y-%m-%d %H:%M', time.gmtime())

    F = open(STAMP, 'w')

    F.write("""\
<html><head>
<meta http-equiv="refresh" content="60"/>
<META HTTP-EQUIV="Expire" content="0">
<style type="text/css">
body {padding: 0; margin: 2px; font-size:-1;}
p,div,pre {padding: 0; margin: 0;}
</style></head><body><pre>""")

    F.write(stampstring)
    F.write(" GMT / " + msg)

    F.write("""</pre></body></html>""")
    F.close()

    print 'Stamp written:', stampstring

if __name__ == '__main__':
    import sys
    msg = ' / '.join(getVersion())
#   if len(sys.argv) >= 1:
#      msg += " / " + " ".join(sys.argv[1:])
    msg += ' / ' + getMirrorHash() + ' / ' + getSpkgHash()
    print 'Message:', msg
    # WARNING: check if second publishing path is in sync with ./go_live.sh and the general layout!!!
    stampfiles = [os.path.join(".", "files", "zzz", "timestamp.html")]
    #stampfiles = [os.path.join('.', 'www', 'mirror', 'zzz', 'timestamp.html'),
    #              os.path.join('..', 'www2', 'mirror', 'zzz', 'timestamp.html')]
    for file in stampfiles:
        writeMirrorTimestamp(msg, file)
