#!/usr/bin/env python
"""
Populate all the source code releases inside download-source.html
"""

print("no longer used")
import sys
sys.exit(0)

import xml.dom.minidom as minidom
import os, sys, time
import utils
from glob import glob

# script uses relative paths, switch to its
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

src_html = os.path.join(".", "www", "download-source.html")
src_dir  = os.path.join(".", "www", "src")
src_old  = os.path.join(".", "www", "src-old")
#src_old  = os.path.join(os.path.sep, "home","was","www","sage_old")
SRC_PATTERN = 'sage-*.tar*'
table_body = None

if not os.path.exists(src_html):
    print('File Not Found: %s' % src_html)
    sys.exit(1)

source_xml = minidom.parse(src_html) 
source = None #this is the target <div id="source">...</div>
divs = source_xml.getElementsByTagName(r'div')
for d in divs:
    if d.getAttribute('id') == r'source':
        source = d

if source is None:
    print('<div id="source">...</div> not found!')
    sys.exit(1)

def initContent():
    global table_body
    #delete everything
    for o in source_xml.getElementsByTagName(r'table'):
       print("deleting", o)
       o.parentNode.removeChild(o)
    table = source_xml.createElement(r'table')
    table.setAttribute(r'class', 'xsmall')
    table_body = source_xml.createElement(r'tbody')
    source.appendChild(table)
    table.appendChild(table_body)
    tr = source_xml.createElement(r'tr')
    for h in [r'Release', r'Source File', r'Size', r'Date']:
        th = source_xml.createElement(r'th')
        th.appendChild(source_xml.createTextNode(h))
        tr.appendChild(th)
    table_body.appendChild(tr)


FILES = glob(os.path.join(src_dir, SRC_PATTERN))
FILESOLD = glob(os.path.join(src_old, SRC_PATTERN))

def writeToSource():
    global table_body
    release = len(FILES) + len(FILESOLD)

    # CURRENT DIRECTORY, BELOW OLD ONES - sorry bad design
    first = True
    FILESnDATES = []
    for F in FILES:
       stat = os.stat(F)
       lastmod = time.localtime(stat[8])
       FILESnDATES.append((lastmod,F))
    FILESnDATES.sort()
    FILESnDATES.reverse()
    for FnD in FILESnDATES:
       F = FnD[1]
       size = int(os.path.getsize(F)/(2**20))
       date = time.strftime('%Y-%m-%d', FnD[0])
       name = F.split(os.path.sep)[-1]
   
       tr = source_xml.createElement(r'tr')
       if first:
           tr.setAttribute(r'class','first')
           first = False
       elif release % 2 == 0:
           tr.setAttribute(r'class', 'even')
       else:
           tr.setAttribute(r'class', 'odd')
   
       td = source_xml.createElement(r'td')
       td.appendChild(source_xml.createTextNode(str(release)))
       tr.appendChild(td)
   
       td = source_xml.createElement(r'td')
       print(name)
       a = source_xml.createElement(r'a')
       a.setAttribute(r'href', F.replace(os.path.sep + r'www', ''))
       a.appendChild(source_xml.createTextNode(name))
       td.appendChild(a)
       tr.appendChild(td) 
       
       td = source_xml.createElement(r'td')
       td.appendChild(source_xml.createTextNode('%s MB'%size))
       tr.appendChild(td)
   
       td = source_xml.createElement(r'td')
       td.appendChild(source_xml.createTextNode(date))
       tr.appendChild(td)
   
       table_body.appendChild(tr)
       release -= 1

    # OLD DIRECTORY - PROBABLY WILL NEVER CHANGE, COULD BE STATIC?
    FILESnDATES = []
    for F in FILESOLD:
       stat = os.stat(F)
       lastmod = time.localtime(stat[8])
       FILESnDATES.append((lastmod,F))
    FILESnDATES.sort()
    FILESnDATES.reverse()
    for FnD in FILESnDATES:
       F = FnD[1]
       size = int(os.path.getsize(F)/(2**20))
       date = time.strftime('%Y-%m-%d', FnD[0])
       name = F.split(os.path.sep)[-1]
   
       tr = source_xml.createElement(r'tr')
       if release % 2 == 0:
           tr.setAttribute(r'class', 'even')
       else:
           tr.setAttribute(r'class', 'odd')
 
       td = source_xml.createElement(r'td')
       td.appendChild(source_xml.createTextNode(str(release)))
       tr.appendChild(td)
   
       td = source_xml.createElement(r'td')
       print(name, F)
       a = source_xml.createElement(r'a')
       a.setAttribute(r'href', 'http://www.sagemath.org/src-old' + F.replace(src_old, ''))
       a.appendChild(source_xml.createTextNode(name))
       td.appendChild(a)
       tr.appendChild(td) 
       
       td = source_xml.createElement(r'td')
       td.appendChild(source_xml.createTextNode('%s MB'%size))
       tr.appendChild(td)
   
       td = source_xml.createElement(r'td')
       td.appendChild(source_xml.createTextNode(date))
       tr.appendChild(td)
   
       table_body.appendChild(tr)
       release -= 1

initContent()
writeToSource()

#print(source_xml.toxml())
#xml.dom.ext.PrettyPrint(source_xml, open(src_html, 'w'))

source_xml.writexml(utils.UnicodeFileWriter( open(src_html, "w")))


#utils.delFirstLine(src_html)

