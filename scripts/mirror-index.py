#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# mirror indexing + md5 sum
# (c) 2009, Harald Schilly, Sage Project
# 
# !!!  IMPORTANT !!!
#            new files with files need an empty $md5file,
#            otherwise no md5sums are calculated!!!
#
#            changed files are not recognized!!!
#
#

import xml.dom.minidom as minidom
import os
import sys
import time
import utils
from hashlib import md5
#import md5
import re


# min_size in MB, below files are not tracked and no md5 sums calculated
MIN_SIZE = 2

# Regular expression for lines in GNU md5sum file
md5line = re.compile(r"^([0-9a-f]{32}) [\ \*](.*)$")
md5file = 'md5sums.txt'

notesfile = 'notes.txt'

# script uses relative paths, switch to its
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# run the indexer for meta files
print "now running meta file indexing, torrents, metalink, or more ..."
print "by calling ./mirror-meta.sh"
print
os.system('./mirror-meta.sh')
print "mirror-meta.sh finished"
print

# this is the name of the subdir, containing torrent and metalinks
METADIR = 'meta'

def create_meta(root):
  """
  uses mktorrent to create torrents with webseeds and the metalink linker. both in ~/bin


  DON'T USE THIS, should replace mirror-meta.sh someday
  """
  print "DON'T USE THIS, it's replaced by mirror-meta.sh"
  return
  root = os.path.abspath(root)
  base = os.path.abspath(root.split(os.path.sep)[-1])
  
  for dir, dirs, files in os.walk(root):
    reldir = dir[len(base):]
    for fn in files:
      f = os.path.join(dir,fn)
      if os.path.getsize(f) < MIN_SIZE * 1024 * 1024: continue
      print ">>> create_meta:", reldir, f
      

  sys.exit(1)


# output filename in each directory
listfile = 'index.html'

# template
outfile = os.path.abspath('mirror-index-template.xml')



def index(root, strip):
    """
    main method, walks through all sub directories,
    for each of them, reads the md5 sums from $md5file
    writes and entry for the table for each file
    below the md5 sum if available or calls for calculating it
    in the end, writes the index.html files for each dir
    """
    for dir, dirs, files in os.walk(root):
        print 'Directory %s' % dir
        if dir == '.' or dir.endswith('meta'):
           continue

        listxml = minidom.parse(outfile)
        el = listxml.getElementsByTagName(u'div')
        output = None
        for e in el:
            if e.getAttribute(u'id') == u'output':
                output = e
                break
        title = listxml.getElementsByTagName(u'title')[0]
        keep = len(dir) - len(root) + len(strip)
        shortdir = dir[-keep:]
        title.appendChild(listxml.createTextNode('SageMath Download - %s' % shortdir))
        
        table = listxml.createElement(u'table')

        table.appendChild(getTableHeaderDir(listxml, shortdir))
        #siblings = [ d for d in os.listdir('..') if os.path.isdir(os.path.join('..', d)) ]
        #table.appendChild(getTableHeaderSiblings(listxml, siblings))

        if notesfile in files:
           table.appendChild(getNotesText(listxml, dir))
           files.remove(notesfile)
  
        tr = getTableRowDir(listxml, dirs)
        table.appendChild(tr)

        #no files (only index.html, hence > 1), no need to list them 
        if len(files) > 1:

          table.appendChild(getTableHeader(listxml))
    
          knownMd5 = readMD5(dir) #reads file

          even = True # even/odd for different backgrounds of table rows
          filesKey = lambda fn:os.path.getmtime(os.path.join(dir,fn))
          for fn in sorted(files, reverse=True, key = filesKey):
              even = not even
              if fn in [listfile, md5file, notesfile]:
                  continue
              f = os.path.join(dir, fn)
              tr = getTableRow(listxml, f, fn, shortdir, even)
              table.appendChild(tr)

              if knownMd5 is not None:# and (os.path.getsize(f) / 1024.0 / 1024.0) > MIN_SIZE:
                isNewer = os.path.getmtime(f) > knownMd5['__MTIME__']
                if isNewer:
                  delMd5Entry(dir, fn)
                if knownMd5.has_key(fn) and not isNewer:
                  trMd5 = getMd5Row(listxml, knownMd5[fn], shortdir, fn, f)
                else:
                  trMd5 = getMd5Row(listxml, calcMd5(dir, fn), shortdir, fn, f)
              else:
                trMd5 = getMd5Row(listxml, None, shortdir, fn, f)
              table.appendChild(trMd5)
            

        output.appendChild(table)
        output.appendChild(trackPageView(listxml, shortdir))
        output_file = os.path.join(dir, listfile)
        if os.path.exists(output_file):
          listxml.writexml(utils.UnicodeFileWriter( open(output_file, "w")))
          print 'written to: %s' % output_file
        else:
          print 'WARNING: file %s does not exist and hence directory information is not written to it' % output_file
        #utils.delFirstLine(output_file)

def trackPageView(xml, shortdir):
     """
     returns a <script> element that tracks this page view
     as an analytics event: "MirrorPV" / "shortdir"
     """
     script = xml.createElement(u'script')
     script.setAttribute(u'type', u'text/javascript')
     js = xml.createTextNode("pageTracker._trackEvent('MirrorPV', '%s', window.location.hostname);" % (shortdir))
     script.appendChild(js)
     return script

def delMd5Entry(dir, fn):
     """
     deletes a md5entry if it has to be recalculated
     """
     print 'del md5 entry', fn
     fn_in = os.path.join(dir, md5file)
     fn_out = os.path.join(dir, md5file + '.tmp')
     md5in = file(fn_in, 'r')
     md5out = file(fn_out, 'a')
     for line in md5in:
        if not line.split()[1] == fn:
            md5out.write(line)
     os.remove(fn_in)
     os.rename(fn_out, fn_in)

def calcMd5(dir, fn):
     """
     if there is no entry in for the given file, it is calculated
     and immediately written to the md5sum file (new line appended)
     """
     md5out = file(os.path.join(dir, md5file), 'a')
     f = file(os.path.join(dir, fn))
     print 'calculating md5 sum of', f.name
     hash = md5()
     while True:
        s = f.read(1048576)
        hash.update(s)
        if s == "":
           break
     f.close()
     print fn, hash.hexdigest()
     md5out.write('%s  %s\n' %(hash.hexdigest(), fn))
     md5out.close()
     return hash.hexdigest()

def readMD5(path):
     """
     reads the $md5sum file and returns a 
     dict({filename: md5sum}) for the index method
     if there is no md5sum file, nothing is returned
     i.e. you need to create an empty $md5sum file for a
     new directory!!!
     Additionally, the key "__MTIME__" contains the creation time
     of them md5sum file.
     """
     f = os.path.join(path, md5file)
     if not os.path.isfile(f):
        return  None
     ret = []
     created = os.path.getmtime(f)
     mtime = time.gmtime(created)
     ret.append(('__MTIME__', created))
     t = time.strftime('%Y-%m-%d %H:%M', (mtime))
     print '  + md5sum file: %s (%s)' % (f, t)
     for line in open(f, 'r').readlines():
        match = md5line.match(line)
        if not match:
            continue
        ret.append((match.group(2), match.group(1)))
     return dict(ret)

def getNotesText(xml, dir):
     """
     inserts the html/text from notes.txt
     """
     from xml.dom.minidom import parse
     fn = os.path.join(dir, 'notes.txt')
     if os.path.exists(fn):
       try:
         notes = parse(fn).firstChild
       except:
         # likely UTF8 error, instead link to file
         notes = xml.createElement(u"a")
         notes.setAttribute(u"href", "notes.txt")
         notes.appendChild(xml.createTextNode(u"For more details, see notes.txt"))
         
       tr = xml.createElement(u'tr')
       td = xml.createElement(u'td')
       td.appendChild(notes)
       td.setAttribute(u'colspan', '4')
       tr.appendChild(td)
       return tr

def getTableHeaderDir(xml, dir):
     """
     the header for the subdirectory info
     """
     th = xml.createElement(u'tr')
     td = xml.createElement(u'th')
     cd = xml.createTextNode(u'Current Directory: %s' % dir)
     td.setAttribute(u'style', u'font-size:large;')
     td.appendChild(cd)
     td.setAttribute(u'colspan', '4')
     th.appendChild(td)
     return th


def getTableHeader(xml):
     """
     describes the three columns
     """
     th = xml.createElement(u'tr')
     th.setAttribute(u'style', 'border-top: 1px solid #c9c9f9;')
     for i in [u'Filename', u'Other', u'Size', u'Date']:
       td = xml.createElement(u'th')
       td.setAttribute(u'id', u'col-' + i)
       if i == 'Metalink':
         a = xml.createElement(u'a')
         a.appendChild(xml.createTextNode(i))
         a.setAttribute(u'href', 'http://wiki.sagemath.org/DownloadAndInstallationGuide')
         td.appendChild(a)
       else:
         td.appendChild(xml.createTextNode(i))
       th.appendChild(td)
     return th

def getMd5Row(xml, md5, shortdir, fn, f):
    """
    the row below the file name, if it is a $MIN_SIZE
    small file, nothing is written
    just there for symmetry
    """
    tr =  xml.createElement(u'tr')
    td = xml.createElement(u'td')
    td.setAttribute(u'class', 'md5')
    if md5 is None:
        td.appendChild(xml.createTextNode(u''))
    else:
        td.appendChild(xml.createTextNode(u'MD5: %s ' % md5))
    tr.appendChild(td)

    tr.appendChild(xml.createElement(u'td'))
    tr.appendChild(xml.createElement(u'td'))
    tr.appendChild(xml.createElement(u'td'))
    return tr 

def getTableRow(xml, f, fn, shortdir, even):
     """
     the row in the table showing the file, link and anaytics tracking
     that's what this is all about in the end!
     """
     created = os.path.getmtime(f)
     size = os.path.getsize(f) / 1024.0 / 1024.0
     t = time.strftime('%Y-%m-%d %H:%M', (time.gmtime(created)))
     print '  + file: %s (%.2f mb, %s)' % (fn, size, t)

     tr = xml.createElement(u'tr')
     tr.setAttribute(u'class', 'even' if even else 'odd') 
     td = xml.createElement(u'td')
     a = xml.createElement(u'a')
     linktext = xml.createTextNode(fn)
     if size > MIN_SIZE: #bold for real files
        bold = xml.createElement(u'strong')
        bold.appendChild(linktext)
        a.appendChild(bold)
     else:    
        a.appendChild(linktext)
     a.setAttribute(u'href', './%s' % fn)
     # onclick="pageTracker._trackEvent(category, action, optional_label, optional_value)
     if size > MIN_SIZE: #only for real files above 2 mb!
        a.setAttribute(u'onclick', u"pageTracker._trackEvent('MirrorDL', '%s', '%s', 1);" % (shortdir, fn))
     td.appendChild(a)
     tr.appendChild(td)
        
     torrentfile = './meta/%s.torrent' % fn
     td = xml.createElement(u'td')
     size = os.path.getsize(f) / 1024.0 / 1024.0
     if size > MIN_SIZE and os.path.exists(os.path.join('..', shortdir, torrentfile)): #only for real files above 2 mb!
        a = xml.createElement(u'a')
        a.appendChild(xml.createTextNode('torrent'))
        a.setAttribute(u'href', torrentfile)
        # onclick="pageTracker._trackEvent(category, action, optional_label, optional_value)
        # torrents are in the same dir as the real download, but show up with a different name (ending .torrent)
        # ie. one torrent download counts as one real download
        a.setAttribute(u'onclick', u"pageTracker._trackEvent('MirrorDL', '%s', '%s.torrent', 1);" % (shortdir, fn))
        td.setAttribute(u'style', u"vertical-align: top;")
        td.appendChild(a)
     tr.appendChild(td)

     # #metalink & zsync file
     # td = xml.createElement(u'td')
     # metafile =  './meta/%s.metalink' % fn
     # #print 'abspath', os.path.abspath(os.path.curdir)
     # #print ' metaf ', metafile
     # #print 'exists?', os.path.join('..', shortdir, metafile)
     # #print '       ', os.path.exists(os.path.join('..', shortdir, metafile))
     # if size > MIN_SIZE and os.path.exists(os.path.join('..', shortdir, metafile)): #only for real files above 2 mb!
     #    a = xml.createElement(u'a')
     #    a.appendChild(xml.createTextNode('metalink'))
     #    a.setAttribute(u'href', metafile)
     #    # onclick="pageTracker._trackEvent(category, action, optional_label, optional_value)
     #    # metalinks are in the same dir as the real download, but show up with a different name (ending .metalink)
     #    # ie. a metalink download counts as one real download
     #    a.setAttribute(u'onclick', u"pageTracker._trackEvent('MirrorDL', '%s', '%s.metalink', 1);" % (shortdir, fn))
     #    td.appendChild(a)
     # tr.appendChild(td)
     # 
     td = xml.createElement(u'td')
     td.appendChild(xml.createTextNode("%.2f MB" % size))
     tr.appendChild(td)

     td = xml.createElement(u'td')
     td.appendChild(xml.createTextNode(t))
     tr.appendChild(td)
     return tr


def getTableRowDir(xml, dirs):
     """
     the row in the table displaying the current directory
     """
     tr  = xml.createElement(u'tr')
     td = xml.createElement(u'th')
     try:
        dirs.remove('meta')
     except ValueError:
        pass
     td.appendChild(xml.createTextNode(u'Subdirectories:' if len(dirs) > 0 else u' '))
     for d in sorted(dirs):
        td.appendChild(xml.createElement(u'br'))
        a = xml.createElement(u'a')
        a.setAttribute(u'href', './%s/index.html' % d)
        a.appendChild(xml.createTextNode(d))
        a.setAttribute(u'style', u'display:inline;font-size:large;')
        td.appendChild(a)
     td.setAttribute(u'colspan', '3')
     tr.appendChild(td)
     return tr
     

if __name__=='__main__':
    #if len(sys.argv) < 2:
    #    print 'first and only argument must be the targt dir from where to index'
    #    sys.exit(1)
    # change to target directory, then all paths are relative from there
    #os.chdir(sys.argv[1])

    # the first www/bin is just for this dir, all later invocations
    # overwrite files generated by this

    #for d in ['./www/bin/', './www/src/', './www/src-old', './www/devel/']:
    #  create_meta(d)
    
    for d in map(os.path.abspath, ['./www/bin/', './www/bin/apple_osx/', './www/bin/microsoft_windows/', './www/bin/linux/', './www/bin/solaris/', './www/src/', './www/src-old/', './www/devel/', './www/spkg/upstream/']):
       os.chdir(d)
       print os.path.abspath(os.curdir)
       strip = d.split(os.path.sep)[-1]
       index(os.path.abspath(os.curdir), strip)

