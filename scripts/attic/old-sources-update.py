#!/usr/bin/env python

import os



#### Create the README file.

r = open('README.txt.in').read()
open('README.txt','w').write(r)

#### Update the web page

PATH="%s/sage/dist/src"%os.environ["HOME"]

F = os.popen("cd %s; ls -1t sage-*"%PATH).read().split('\n')

#F = os.listdir(PATH)
#G = [(os.path.getctime(f), f) for f in F]
#print(G)
#G.sort(reverse=True)
#print("-----\n\n")
#print(G)
#F = [f for _, f in G]

#F.sort()
#F.reverse()

F = [x for x in F if x.find(".py") == -1 and x.find(".html") == -1 and x != "sageonly.tar.gz" and x.find("build_times") == -1 and x.find("README")==-1]

g = open(PATH+"/index.html","w")
g.write("""<html><head><meta http-equiv="content-type" content="text/html;charset=iso-8859-1"><title>SAGE Source Distribution</title>
<LINK REL=STYLESHEET TYPE="text/css" 
      HREF="/was.css" TITLE="was">
</head>
<body>
<h1 align=center><a href="../..">SAGE</a> Source Distribution</h1>
<hr>
<!--<h2 align=center>Instructions</h2>-->
<div align=center>
<table>
<tr><td>
<ol>
<li> Download a recent  source distribution from the top of the list below.
See the <a href="changelog.txt">changelog</a>.

<li> Extract and build SAGE, as explained in
<a href="../../doc/html/inst/">the installation guide.</a>

</ol>
</td></tr></table>
</div>
<hr>

<!--
If you just want to update a current SAGE install to the latest SAGE source,
go to the top level sage directory and type "make web-update" at the shell
prompt.
This should work with complete installs of SAGE from 2005-04-21 onward,
but not with previous versions.  This assumes you have wget installed.
-->
""")

g.write('<table align=center border=0 cellpadding=10 bgcolor="black">\n')
for x in F:
    size = int(os.path.getsize(PATH + "/" + x)/1000000)
    if x == "sage.tar.bz2" or not x[:5] == 'sage-':
        continue
    print(x)
    name = x.replace("_"," ").replace("sage-","")
    i = name.find("-src")
    if i != -1:
        name = name[:i]
    name = "&nbsp;"*5 + name + "&nbsp;"*5
    if name.find("pre") != -1:
        name += "<i><b>(experimental!)</b></i>"
    g.write('<tr><td align=center bgcolor="#FFFFF0"><a href="%s">%s</a></td><td bgcolor="#FFFFF0"> %s MB</td></tr>\n'%(x,name,size))

g.write('</table>')

g.write('</body></html>')
    
