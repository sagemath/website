#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Geocoding Sage Developers

Use this script to parse location in ack.xml and store the locations.
Just geotagging online works, but is slow and could make errors.

additionally, one IP is only allowed to handle 15.000 requests per day
and not too fast (we slow things down!)

BUGS:
 * devcloud tag get's shortend, firefox&co cannot cope with it :( ... make it full again
"""

import xml.dom.minidom as minidom
from xml.dom.minidom import parse, parseString
import os
from os.path import join
import sys
import urllib
import urllib2
import time
import utils

# script uses relative paths, switch to its
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# google key for sagemath.org - got free from their maps api website
#gkey   = "ABQIAAAA9l-aWy6wHEH5peWCry_l4hQm4J-jBIjYt60ld8MMTn6uhPOgVhSg6NCleXrEpyNFs6aDpgXODBd72w"
#gkey = "AIzaSyCh9JDXJE7BsdfT105pRP_dusAzxadA_kc"
gkey = "AIzaSyB3YiQ---yL6-QfoW9heq4-VbrAQzerhhA"

# allowed attributes in source xml, for checkXML
goodKeys = ["name", "location", "work", "description", "url", "pix", "size", "jitter", "trac"]

# point to datafiles in local path, ./www/res/... should be best
ack = parse(join("..", "conf", "contributors.xml"))
geocode_xml_outfn = join("..", "conf", "geocode.xml")
devmap_tmpl = os.path.join("..", "templates", "devs.html")
devlist = None
tracSearch = "http://trac.sagemath.org/sage_trac/search?q="

devmap = minidom.Document()

# def getDevlist():
#    devlists = devmap.getElementsByTagName(r'tbody')
#    for d in devlists:
#        if d.getAttribute('id') == r'devlist':
#            return d

if os.path.exists(geocode_xml_outfn):
    locxml = parse(geocode_xml_outfn)
else:
    locxml = minidom.Document()

loclist = locxml.getElementsByTagName("loc")
timeout = 30  # in secs, timeout between each request to avoid error 620


def writeToDevmap():
    """
    we assume that everything is written to the xml file and we have all data.
    """
    # cleanup
    # for d in devlist.childNodes:
    #    d.parentNode.removeChild(d)
    #devlist = getDevlist()
    #p = devlist.parentNode
    # p.removeChild(devlist)
    tbody = devmap.createElement(r'tbody')
    tbody.setAttribute(r'id', r'devlist')
    devmap.appendChild(tbody)
    devlist = tbody

    # fixing empty tag
    # for d in devmap.getElementsByTagName(r'div'):
    #    if d.getAttribute('id') == r'devcloud':
    #        devcloud = d
    devcloud = devmap.createElement(r'div')
    devcloud.setAttribute("id", "devlist")
    devcloud.appendChild(devmap.createTextNode(" "))

    # write from ack file, and we don't need geolocations
    for c in ack.getElementsByTagName("contributors")[0].childNodes:
        if c.nodeType != ack.ELEMENT_NODE:
            continue
        if c.tagName != "contributor":
            continue
        dev = c.getAttribute("name")
        loc = c.getAttribute("location")
        work = c.getAttribute("work")
        descr = c.getAttribute("description")
        url = c.getAttribute("url")
        trac = c.getAttribute("trac")

        tr = devmap.createElement("tr")
        td = devmap.createElement("td")
        if len(url) == 0:
            td.appendChild(devmap.createTextNode(dev))
        else:
            a = devmap.createElement("a")
            a.setAttribute("href", url)
            a.appendChild(devmap.createTextNode(dev))
            td.appendChild(a)
        td.setAttribute("class", "name")
        tr.appendChild(td)
        td = devmap.createElement("td")
        if len(work) != 0:
            td.appendChild(devmap.createTextNode(work))
        tr.appendChild(td)
        td = devmap.createElement("td")
        if len(loc) != 0:
            td.appendChild(devmap.createTextNode(loc))
        tr.appendChild(td)
        td = devmap.createElement("td")
        if len(descr) != 0:
            descr = map(lambda _: _.strip(), descr.split(r';'))
            first = True
            for d in descr:
                if not first:
                    td.appendChild(devmap.createElement("br"))
                else:
                    first = False
                # since there are tags in the string, we parse it
                d = d.replace("&lt;", "<").replace("&gt;", ">")
                d_el = parseString("<span>%s</span>" % d)
                td.appendChild(d_el.firstChild)

        if len(trac) == 0:
            trac = dev
        trac = trac.replace(" ", "%20")
        a = devmap.createElement("a")
        a.setAttribute("href", tracSearch + trac)
        a.setAttribute("class", "trac")
        #a.setAttribute("target", "_blank")
        a.appendChild(devmap.createTextNode("contributions"))
        td.appendChild(devmap.createElement("br"))
        td.appendChild(a)

        td.setAttribute("class", "description")
        tr.appendChild(td)
        devlist.appendChild(tr)


def checkXML():
    for c in ack.getElementsByTagName("contributors")[0].childNodes:
        if c.nodeType != ack.ELEMENT_NODE:
            continue
        if c.tagName != "contributor":
            raise Exception("wrong tag name: %s" % c.tagName)
    for c in ack.getElementsByTagName("contributor"):
        at = c.attributes.keys()
        for a in at:
            if a not in goodKeys:
                raise Exception("wrong Key: %s" % a)

checkXML()


# if geocode_xml_outfn exists, read in dict of locations to nodes, else empty
def locExists(loc):
    for l in loclist + out.getElementsByTagName("loc"):
        if l.getAttribute("location") == loc:
            return l
    return None

outxml = minidom.Document()
outxml.appendChild(outxml.createElement("locations"))
out = outxml.firstChild

comment = outxml.createComment("ATTENTION: DON'T EDIT THESE LOCATIONS. AUTOMATICALLY CREATED BY " + sys.argv[0])
out.appendChild(comment)


def getGeo(loc):
    """
    CSV Geo returns: [200,6,42.730070,-73.690570]
    [retcode,accuracy,lng,lat]
    """
    loc = loc.replace(" ", "+")
    loc = urllib2.quote(loc.encode('UTF-8'))
    print loc, ">>>",
    global timeout
    print "[doing query, %s secs break] >>>" % timeout,
    sys.stdout.flush()
    time.sleep(timeout)
    #url = 'http://maps.google.com/maps/geo?q=%s&output=csv&key=%s' % (loc, gkey)
    #url = ' https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (loc, gkey)
    url = ' https://maps.googleapis.com/maps/api/geocode/json?address=%s' % loc
    geo = (urllib.urlopen(url)).read()
    import json
    geo = json.loads(geo)
    acc = "6"  # no idea
    # no results? (new error in 2018)
    if len(geo["results"]) == 0:
        return None
    # print geo
    loc = geo["results"][0]["geometry"]["location"]
    lng = str(loc["lng"])
    lat = str(loc["lat"])
    print acc, lng, lat
    return "200", acc, lat, lng


def addGeo(place):
    lcache = locExists(place)
    attempts = 5
    if not lcache:
        geo = getGeo(place)
        while geo is None and attempts > 0:
            print "[no result, trying again] >>>",
            sys.stdout.flush()
            geo = getGeo(place)
            attempts -= 1
        if geo is None and attempts == 0:
            print "FAILURE AFTER TOO MANY ATTEMPTS"
            return
        g = outxml.createElement("loc")
        statuscode = geo[0]
        # http://code.google.com/apis/maps/documentation/reference.html#GGeoStatusCode
        # 620 means too fast, we need to slow down!
        if "620" == statuscode:
            print "we were too fast, error code 620 by google!"
            global timeout
            timeout *= 2
            addGeo(place)
        elif "200" != statuscode:
            raise Exception("Status Code was not 200, but %s\nPlace: %s\nGeo: %s" % (statuscode, place, ",".join(geo)))
        else:  # code must be 200!
            # insert the same for matching later
            g.setAttribute("location", place)
            g.setAttribute("loclng", geo[2])
            g.setAttribute("loclat", geo[3])
            out.appendChild(g)
    else:
        print "cache"
        out.appendChild(lcache)


def getStatistics():
        # get statistics for description
    nbContribs = len(ack.getElementsByTagName("contributor"))
    nbPlaces = len(out.getElementsByTagName("loc"))
    # for c in devmap.getElementsByTagName('span'):
    #    if c.getAttribute("id") == "contrib-nb":
    #        c.replaceChild(devmap.createTextNode(str(nbContribs)), c.childNodes[0])
    #    elif c.getAttribute("id") == "contrib-places":
    #        c.replaceChild(devmap.createTextNode(str(nbPlaces)), c.childNodes[0])
    print "contributors =", str(nbContribs), "places =", str(nbPlaces)
    return nbContribs, nbPlaces

# read through ack.xml
for c in ack.getElementsByTagName("contributor"):
    print c.getAttribute("name"), ">>>",
    if c.hasAttribute("location"):
        addGeo(c.getAttribute("location"))
    else:
        print "  <--- UNKNOWN LOCATION !!!"


print
print "This is now written to file %s:" % geocode_xml_outfn
print out.toprettyxml()

#xml.dom.ext.PrettyPrint(out, open(geocode_xml_outfn, "w"))
out.writexml(utils.UnicodeFileWriter(open(geocode_xml_outfn, "w")), newl="\n")

print
print "calculating statistics and writing to description"
nbContribs, nbPlaces = getStatistics()

print
print "now writing table entries for search engines and javascript disabled ones"
writeToDevmap()

print "file written to %s" % devmap_tmpl
#xml.dom.ext.PrettyPrint(devmap, open(devmap_xml, "w"))
#devmap.writexml(utils.UnicodeFileWriter(open(devmap_tmpl, "w")), newl="\n")
# utils.delFirstLine(devmap_xml)
import codecs
with codecs.open(devmap_tmpl, "w", "utf8") as outf:
    outf.write("{% macro number() %}" + str(nbContribs) + "{% endmacro %}")
    outf.write("{% macro places() %}" + str(nbPlaces) + "{% endmacro %}")
    outf.write("""{% macro devs() %}
    """)
    x = devmap.toprettyxml(encoding="utf8", indent=" ", newl="\n").decode("utf8")
    x = x.split("\n", 1)[1]
    outf.write(x)
    outf.write("""{% endmacro %}
    """)
