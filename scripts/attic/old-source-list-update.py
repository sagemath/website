#!/usr/bin/env python

import os, time


#### Create the README file.


#r = open('README.txt.in').read()
#open('README.txt','w').write(r)

#### Update the web page

PATH=os.path.abspath('.')

F = os.popen("ls -1t sage-*").read().split('\n')

F = [x for x in F if os.path.isfile(x) and x.find(".py") == -1 and \
     x.find(".html") == -1 and x != "sageonly.tar.gz" and \
     x.find("build_times") == -1 and x.find("README")==-1 and \
     not ('mindist' in x) ]

G = [x for x in F if not ('mindist' in x)]

open("LATEST",'w').write(G[0])

g = open(PATH+"/index.html","w")
g.write("""<html><head>
	<meta http-equiv="content-type" content="text/html;charset=iso-8859-1">
	<title>Sage Source Distribution</title>
<LINK REL=STYLESHEET TYPE="text/css" 
      HREF="/was.css" TITLE="was">
</head>
<body>
<h1 align=center><a href="../..">Sage</a> Source Distribution</h1>
<hr>
<!--<h2 align=center>Instructions</h2>-->
<div align=center>
<table>
<tr><td>
<ol>
<li> Thank you for downloading Sage!
Please read the <a href="README.txt">README.txt</a>.

<li> Get sage-x.y.z.tar for a standalone Sage install that includes
"all" dependencies and builds on OS X and Linux.

<li> Extract and build Sage, as explained in
<a href="../doc/inst/inst.html">the installation guide.</a>

<li> There is a very high level <a href="changelog.txt">changelog</a>.

<li> You can 
<a href="http://www.sagemath.org/hg/">browse all the
tracked source code repositories</a> and see exactly what's going on, and
who did what when.

</ol>
</td></tr></table>
</div>
<hr>

<!--
If you just want to update a current Sage install to the latest Sage source,
go to the top level sage directory and type "make web-update" at the shell
prompt.
This should work with complete installs of Sage from 2005-04-21 onward,
but not with previous versions.  This assumes you have wget installed.
-->
""")

g.write('<table align=center border=0 cellpadding=10 bgcolor="black">\n')

H = [x for x in F if x.startswith('sage-')]
release_number = len(H)

for x in H:
    size = int(os.path.getsize(PATH + "/" + x)/(2**20))
    name = x.replace("_"," ")
    i = name.find("-src")
    if i != -1:
        name = name[:i]
    #name = "&nbsp;"*5 + name + "&nbsp;"*5
    if name.find("pre") != -1:
        name += "<i><b>(experimental!)</b></i>"
    date = time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(PATH+'/'+x)))
    g.write('<tr><td bgcolor="#fffff0">Release %s</td> <td align=left bgcolor="#FFFFF0"><a href="%s">%s</a></td><td bgcolor="#FFFFF0"> %s MB</td> <td bgcolor="#FFFFF0"> %s </td></tr>\n'%(release_number, x,name,size,date))
    release_number -= 1

g.write('</table>')

g.write('<hr><center><a href="http://modular.ucsd.edu/sage_old">Click for old version archive.</a></center>')

g.write('</body></html>')
    
