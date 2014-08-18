#!/usr/bin/env python

#this script generates zsync files

# zsyncmake -e -v -b 1024 [ -u http://... for each mirror ] FILE.tar.gz -o meta/FILE.tar.gz.zsync

import os, sys

print "zsync doesn't work ... this file is just for reference"
sys.exit(1)

# script uses relative paths, switch to its
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

basecmd = 'zsyncmake -e -v -b 1024 '
rootdir = './www/mirror/'
roots = map(os.path.expanduser, ['./www/mirror/livecd', './www/mirror/win', './www/mirror/linux', './www/mirror/osx', './www/mirror/solaris', './www/mirror/src'])

# get the URLs for the mirrors
mirrors =  []
with open(os.path.expanduser('~/www2-dev/www/metalink.helper')) as f:
  for l in f:
    url = l.split('%')[1].strip()
    mirrors.append(url)

#print mirrors

def mirrorcmd(p, fn):
  p = p[len(rootdir):]
  return ' '.join(['-u %s%s/%s' % (_,p,fn) for _ in mirrors])



for root in roots:
  for dir, dirs, files in os.walk(root):
    if not 'meta' in dirs:
       continue
    print 'Directory %s' % dir
    for fn in files:
       f = os.path.join(dir, fn)
       if fn.endswith('zsync'):
          continue
       z = os.path.join(dir, 'meta', fn) + '.zsync'
       if os.path.exists(z):
          print 'skipped file already exists: %s' % z
          continue
       if os.path.getsize(f) < 1024*1024*10:
          continue
       print 'Calling zsync on ', f
       m = mirrorcmd(dir, fn)
       cmd = basecmd + m + ' ' + f + ' -o ' + z 
       #print 'executing:', cmd
       os.system(cmd)
