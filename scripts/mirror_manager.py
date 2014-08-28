#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This script manages Sage Mirrors

Featues:
 - tests if they are online
 - tests if they are in sync
 - generates suiteable download page for the website + python list
 
 Aim:
 - don't present outdated or offline mirrors to the downloader
 - provide list of up-to-date mirrors (i.e. eval(urllib.urlopen(...).read())

Notes:
 - you don't have to publish the page with go_live, see "TARGET" variable below
 - script is designed to be called by crontab every 10 minutes
   to edit the crontab entry, do "$ crontab -e" as user sage and enter this line:
*/10 * * * * /home/sage/www2-dev/mirror_manager.py 2> /home/sage/www2-dev/mirror_manager.error > /home/sage/www2-dev/mirror_manager.out
or better the wrapper script to ensure, that only on instance runs at the same time
*/10 * * * * /home/sage/www2-dev/mirror_manager_wrapper.sh

COPYRIGHT: Harald Schilly <harald.schilly@gmail.com>, 2009, Vienna, Austria
LICENSE: GPL2+
'''

import urllib2
# import subprocess #we use curl, urllib2.urlopen doesn't work :(
import re
import time
from threading import Thread
import string
import os
from os.path import join, normpath
import sys
import time

# safeguad, don't run script two times at the same time
# there is something very odd, probably nfs file system and
# vm ware and stuff like that -> no, it was the open socket
# problem, that's not exposed in urllib, see below.
# the wrapper script uses gnu's
# flock -xn ./lockfile python script.py RUNME
# to ensure that only one instance is running
if len(sys.argv) <= 1 or sys.argv[1] != 'RUNME':
    print('ERROR: USE THE ', sys.argv[0], '_wrapper.sh SCRIPT !!!')
    sys.exit(1)

# everything stalls sometimes since timetouts are not part of urllib!
# http://viralcontentnetwork.blogspot.com/2007/08/handling-timeouts-with-urllib2-in.html
import socket
socket.setdefaulttimeout(10)

# script uses relative paths, switch to its
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

##################### constants and data #######################

TIMESTAMP_SUFFIX = "zzz/timestamp.html"
TIMESTAMP_RE = re.compile(r'<pre>(.*)</pre>')
DELIM_RE = re.compile(r' / ')

# where the output file is written to
OUTDIR = join("..", "templates")
TARGETS = [join(OUTDIR, 'mirrorselector.html')]
TARGETS_SPKG = [join(OUTDIR, 'mirrorselector-src.html')]
TARGETS_LIST = ['mirror_list']
OUTPUT_FILE = 'mirror_manager.out'
METALINK_FILE = ['metalink.helper']
TORRENT_FILE = ['torrent.helper']

# mirrors.html holds the list of all mirrors
# the are inserted between <!--STARTTOKEN--> and <!--ENDTOKEN-->
MIRRORS_HTML = join(OUTDIR, 'all-mirrors.html')
tslog = time.strftime('%Y-%U', time.gmtime())
LOGFILE = './mirror-log/mirror_manager_%s.log' % tslog
SYMLINK = './mirror-log/mirror_manager.log'
if os.path.islink(SYMLINK):
    os.remove(SYMLINK)
os.symlink('./mirror-log/mirror_manager_%s.log' % tslog, SYMLINK)
OUTPUT = ''

# categories of the mirror list, used to group the mirrors
CATEGORY = {
    "g": " Global",
    "na": "America, North",
    "sa": "America, South",
    "e": "Europe",
    "a": "Asia",
    "af": "Africa",
    "aus": "Australia"
}


class Mirror():

    """
    mirror class contains all info needed to
    contact and analyze a mirror
    """

    def __init__(self, name, cat, flag, url, active, country='', priority=50):
        if cat not in CATEGORY:
            raise RuntimeError('category %s does not exist' % cat)
        if not isinstance(active, bool):
            raise RuntimeError('type(active) is not bool')
        self.name = name
        assert cat in CATEGORY.keys()
        self.cat = cat
        assert url.endswith("/")
        self.url = url
        self.active = active
        if country is None or country == '':
            self.country = url.split(r'/')[2].split(r'.')[-1]
        else:
            self.country = country
        self.flag = flag if flag is not None else self.country
        self.priority = priority

    def entry(self):
        n = self.name
        f = '<img src="http://www.sagemath.org/pix/flags/%s.png" width="22" height="14"></img>' % self.flag
        return '<a href="%s{{ mirrordir }}/index.html">%s %s</a>\n' % (self.url, f, n)


# base URLs of all mirrors [("name", "category", "flag", "url", "active"), ...]
# active: True or False (False means that it will be ignored)
# priority for metalinks, default 50; country for metalinks geolocation hint (default end of server url)
MIRRORS = [
    #Mirror("UW2 (WA, USA)", "na", "us", "http://sage.math.washington.edu/sage/", True, priority=1, country='us'),
    Mirror("University of Washington, Seattle, WA, USA", "na", "us", "http://boxen.math.washington.edu/home/sagemath/sage-mirror/", True, priority=1, country='us'),
    #Mirror("CoralCDN", "g", 1, "http://sage.math.washington.edu.nyud.net/sage/", True),
    Mirror("Harvard, Boston, MA, USA", "na", "us", "http://modular.fas.harvard.edu/sage/", True, priority=10, country='us'),
    Mirror("James Madison University, VA, USA", "na", "us", "http://modular.math.jmu.edu/", True, country='us'),
    Mirror("XMission, Utah, USA", "na", "us", "http://mirrors.xmission.com/sage/", True, country='us', priority=75),
    Mirror("Technocozy, MD, USA", "na", "us", "http://sage.technocozy.com/", True, country='us'),
    Mirror("Simon Fraser University, B.C., Canada", "na", "ca", "http://www.cecm.sfu.ca/sage/", True),
    Mirror("SciPy, TX, USA", "na", "us", "http://sage.scipy.org/sage/", True, country='us'),
    # utk mirror lost due to shutdown request by uni administration
    #Mirror("University of Tennessee, TN, USA", "na", "us", "http://mira.sunsite.utk.edu/sagemath/", True, country='us', priority=20),
    Mirror("Universidade Federal do Paraná, Brazil", "sa", "br", "http://sagemath.c3sl.ufpr.br/", True),
    Mirror("SWITCHmirror, Zurich, Switzerland", "e", "ch", "http://mirror.switch.ch/mirror/sagemath/", True, priority=90),
    Mirror("Technical University, Prague, Czech", "e", "cz", "http://ftp.sh.cvut.cz/MIRRORS/sagemath/", True),
    Mirror("Freie Universität Berlin, Germany", "e", "de", "ftp://ftp.fu-berlin.de/unix/misc/sage/", True),
    Mirror("University of Sydney", "aus", "au", "http://echidna.maths.usyd.edu.au/sage/", True, country='au'),
    Mirror("AARNet Research Network", "aus", "au", "http://mirror.aarnet.edu.au/pub/sage/", True),
    Mirror("Riken, Japan", "a", "jp", "http://ftp.riken.jp/sagemath/", True),
    Mirror("Yandex, Russia", "a", "ru", "http://mirror.yandex.ru/mirrors/sage.math.washington.edu/", True),
    Mirror("KAIST, Republic of Korea", "a", "kr", "http://ftp.kaist.ac.kr/sage/", True),
    Mirror("Yongbok, Republic of Korea", "a", "kr", "http://mirror.yongbok.net/sage/", True),
    Mirror("Stellenbosch University, South Africa", "af", "za", "ftp://ftp.sun.ac.za/pub/mirrors/www.sagemath.org/", True),
    Mirror("Jember University, Java, Indonesia", "a", "id", "http://mirror.unej.ac.id/mirrors/sage/", True),
    Mirror("RedIRIS Research Network, Spain", "e", "es", "http://sunsite.rediris.es/mirror/sagemath/", True),
    Mirror("Polytechnic of Namibia", "af", "na", "http://sagemath.polytechnic.edu.na/", True),
    Mirror("University of Cape Town, South Africa", "af", "za", "http://ftp.leg.uct.ac.za/pub/packages/sage/", True, priority=10),
    Mirror("Mirrorservice Network, United Kingdom", "e", "gb", "http://www.mirrorservice.org/sites/www.sagemath.org/", True, country='uk'),
    Mirror("Universidade do Porto, Portugal", "e", "pt", "http://mirrors.fe.up.pt/pub/sage/", True),
    Mirror("Εθνικό Μετσόβιο Πολυτεχνείο, Greece", "e", "gr", "http://ftp.ntua.gr/pub/sagemath/", True),
    Mirror("Wuala (Content Distribution Network)", "e", "ch", "http://content.wuala.com/contents/phatsphere/edoras/sage-mirror/", False),
    Mirror("Tertiary Education Network, Johannesburg, South Africa", "af", "za", "http://sagemath.mirror.ac.za/", True),
    Mirror("Yaşar Üniversitesi, Turkey", "a", "tr", "http://sage.yasar.edu.tr/", True),
    Mirror("Indian Institute of Technology Madras, India", "a", "in", "http://ftp.iitm.ac.in/sage/", True),
    Mirror("Université Pierre et Marie Curie, Paris, France", "e", "fr", "http://www-ftp.lip6.fr/pub/math/sagemath/", True),
    Mirror("Université du Québec à Montréal, Québec, Canada", "na", "ca", "http://mirror.clibre.uqam.ca/sage/", True),
    Mirror("Tunisia", "af", "tn", "http://sagemath.mirror.tn/", True),
    Mirror("Nanyang Technological University, Singapore", "a", "sg", "http://jambu.spms.ntu.edu.sg/sage/", True),
    Mirror("GARR, Italy", "e", "it", "http://sage.mirror.garr.it/mirrors/sage/", True),
    Mirror("Tallinn, Estonia", "e", "ee", "http://servingzone.com/mirrors/sage/", True),
    Mirror("Sofia, Bulgaria", "e", "bg", "http://sage.Igor.onlineDirect.bg/", True),
    # name should include the university by request!
    Mirror("Tsinghua University, Beijing, China", "a", "cn", "http://mirrors.tuna.tsinghua.edu.cn/sagemath/", True),
    Mirror("WIDE Project Tsukuba NOC, Japan", "a", "jp", "http://ftp.tsukuba.wide.ad.jp/software/sage/", True),
    Mirror("University of São Paulo, Brazil", "sa", "br", "http://linorg.usp.br/sage/", True),
    Mirror("University of Science and Technology, China", "a", "cn", "http://mirrors.ustc.edu.cn/sagemath/", True),
    Mirror("Huazhong University of Science and Technology, China", "a", "cn", "http://mirrors.hustunique.com/sagemath/", True),
    Mirror('Hub.co Services Inc., NY, USA', 'na', 'us', "http://mirrors.hub.co/sage/", True),
    Mirror('Huazhong University of Science and Technology, Hubei, China', 'a', 'cn', "http://mirror.hust.edu.cn/sagemath/", True),
    Mirror('Google Datacenter, EU', 'e', 'eu', 'http://www-eu-1.sagedev.org/mirror/', True),
    Mirror("ASIS, Theran, IR", "a", "ir", "http://sage.asis.io/", True)
]

TOTAL_NUMBER = len(MIRRORS)

# define master server as Seattle. this one is the "Correct" one.
# it's also the master if it is not active, see lines below to be invisible but still used as the reference
# TODO: maybe, it's better to automatically define the most recent one as the master? - currently NO!
MASTER = MIRRORS[0]

# filter only actives
MIRRORS = [_ for _ in MIRRORS if _.active]

# intro text
TS_INTRO = r"""
{# ATTENTION: THIS FILE IS AUTOGENERATED BY mirror_manager.py #}
{% macro mirrors(mirrordir) %}
Please select a download server close to your location below.
"""

TS_OUTRO = """
{% endmacro %}
"""
#r"""You can see the full list of mirror servers <a href="./mirrors.html">here</a>."""

# syncing info
TS_SYNC = r"""
<br/>
<strong>Download servers in the mirror network are currently synchronizing. Please try again later.</strong>
"""
TS_NEW = r"""
<br/>
<strong>A new release</strong> is upcoming. Maybe come back later for the next version of Sage.
"""

# delimiter sign
TS_DELIM = r"""&middot;"""

################# functions ####################


def info(txt, width=127):
    """
    helper function
    """
    global OUTPUT
    OUTPUT += '\n' + '=' * width + '\n'
    OUTPUT += ' ' + string.center(txt, width - 4) + '\n'
    OUTPUT += '-' * width + '\n'


def log(mirrors):
    ts = '%4s%2s%2s-%2s:%2s:%2s' % time.gmtime()[0:6]
    f = open(LOGFILE, 'a')
    try:
        f.write(ts)
        f.write(';')
        for m in sorted(mirrors, key=lambda x: x.name):
            f.write(m.name)
            f.write(';')
        f.write('\n')
    finally:
        f.close()


def mirrors_html():
    """
    this function inserts *all* mirrors between the START and ENDTOKENS
    in the html code of MIRRORS_HTML

    there are two templates for the headings and the entries in the table

    algorithm:
    first, the header is read (HEADER, state 0)
    then nothing is done until the ENDTOKEN comes (state 1)
    in the end, everything else is stored in FOOTER (state 2)

    return is HEADER + generated list + FOOTER
    """
    from string import Template
    section = Template("""
<tr>
 <td><h2>${NAME}</h2></td>
</tr>
""")

    entry = Template("""
<tr>
 <td>
     <img alt="" src="${URL}sageicon.png" width="16" height="16" />
     <a href="${URL}index.html">${NAME}</a>
 </td>
</tr>
<tr>
 <td><iframe scrolling="no" src="${URL}zzz/timestamp.html"></iframe></td>
</tr>
""")

    # now building the list
    LIST = ""
    sm = sorted(MIRRORS, key=lambda x: x.name)
    for c in sorted(CATEGORY.iteritems(), key=lambda x: x[1]):
        selected_mirrors = [entry.substitute(URL=m.url, NAME=m.name) for m in sm if m.cat == c[0]]
        if len(selected_mirrors) > 0:
            LIST += section.substitute(NAME=c[1])
            # per category, mirrors sorted by name
            LIST += '\n'.join(selected_mirrors)
    return LIST


# TODO urllib.quote(u) -- replace spaces by %20 and more ... (use this everywhere!)
def fetch_timestamps():
    """
    fetches the timestamps in parallel,
    @return map of mirror <-> timestamp.html file
    """
    info("fetching timestamps in parallel")
    ret = {}

    def stdout(msg):
        sys.stdout.write("  " + msg)
        sys.stdout.flush()

    def fetch_task(mirror):
        global OUTPUT
        time1 = time.time()
        try:
            response = urllib2.urlopen(mirror.url + TIMESTAMP_SUFFIX)
            ret[mirror] = response.read()
            m = '%8.2f [ms] %s\n' % ((time.time() - time1) * 1000.0, mirror.name)
            OUTPUT += m
            stdout(m)
        except Exception as err:  # urllib2.URLError, err:
            if True:  # err_count > 5:
                m = '%8.2f [ms] %s' % ((time.time() - time1) * 1000.0, mirror.name)
                m += " -> %s\n" % str(err)
                OUTPUT += m
                stdout(m)

    tasks = []
    for mirror in MIRRORS:
        t = Thread(target=fetch_task, args=(mirror,))
        t.start()
        tasks.append(t)
        time.sleep(0.1)

    for t in tasks:
        t.join(timeout=50)  # a bit more than the socket timeout
    return ret


def extract_timestamps(TS):
    """
    extracts the actual timestamp from timestamp.html
    """
    info("extracting timestamps")
    ret = {}
    global OUTPUT
    for mirror in sorted(TS.keys(), key=lambda m: m.name):
        ts = TS[mirror]
        t = TIMESTAMP_RE.search(ts)
        if not t is None and len(t.groups()) > 0:
            OUTPUT += "%-20s %s\n" % (mirror.name, t.group(1))
            ret[mirror] = t.group(1)
        else:
            OUTPUT += "%-20s %s\n" % (mirror.name, "TIMESTAMP RETRIVAL ERROR (404 page, garbage, ...)")
    return ret


def dissect_timestamps(TS):
    """
    dissects timestamps based on their specific format
    into individual tokens for later analysis
    """
    from datetime import datetime
    info("dissecting timestamps")
    global OUTPUT
    ret = {}
    for mirror in sorted(TS.keys(), key=lambda m: m.name):
        tokens = DELIM_RE.split(TS[mirror])
        if not tokens is None and len(tokens) >= 3:
            time = datetime.strptime(tokens[0], '%Y-%m-%d %H:%M %Z')
            if len(tokens) == 3:
                OUTPUT += "%-20s %-5s %-5s \n" % (mirror.name, tokens[1], tokens[2])
                ret[mirror] = (tokens[1], tokens[2], " ", time)
            elif len(tokens) == 4:
                OUTPUT += "%-20s %-5s %-5s %s\n" % (mirror.name, tokens[1], tokens[2], tokens[3])
                ret[mirror] = (tokens[1], tokens[2], tokens[3], time)
            elif len(tokens) == 5:
                OUTPUT += "%-20s %-5s %-5s %s %s\n" % (mirror.name, tokens[1], tokens[2], tokens[3], tokens[4])
                ret[mirror] = (tokens[1], tokens[2], tokens[3], time, tokens[4])
        else:
            OUTPUT += mirror[0], "ERROR, len(tokens)=%s\n" % (len(tokens))
    return ret


def find_reference(TS):
    """
    finds reference tokens, for now MASTER, the most recent timestamp counts
    """
    info("selecting reference timestamp")
    global OUTPUT
    # instead of return TS[MASTER][2]
    # of all timstaps, sort them by date, get the *last* one and return the hashcode
    ref = sorted(TS.iteritems(), key=lambda _: _[1][3])[-1]
    OUTPUT += '%s @ %s selected\n' % (ref[0].name, ref[0].url)
    return ref[1][2], ref[1][4]


def good_mirrors(TS, ref):
    """
    returns list of good mirrors, that's what this is all about!
    """
    info("compiling list of good mirrors")
    good = []
    global OUTPUT
    for mirror in sorted(TS.keys(), key=lambda m: m.name):
        if TS[mirror][2] == ref:
            good.append(mirror)
            OUTPUT += '+ %s\n' % mirror.name
        else:
            OUTPUT += '- %s rejected\n' % mirror.name
    OUTPUT += '\n'
    # remove master (Seattle), if we have more than half synced mirrors in North America
    # AND the number of all synced mirrors is more than half of all mirrors
    # saves bandwidth for all the other serivces hosted there.
    # if len([m for m in good if m.cat=='na']) > len([m for m in MIRRORS if m.cat=='na'])/2 and len(good) > TOTAL_NUMBER/2:
    # option B, remove MASTER, if there is another one in North America, more aggressive...
    # if len([m for m in good if m.cat=='na']) >= 2:
    #  OUTPUT +=  'removed master (Seattle), to save bandwidth for other services,\n'
    #  OUTPUT +=  'since there are other servers in North America available...\n'
    #  if MASTER in good:
    #    good.remove(MASTER)
    # if MIRRORS[1] in good and MIRRORS[0] in good:
    #  good.remove(MIRRORS[1])
    #  OUTPUT += 'removed secondary UW mirror, since the primary one is online\n'
    return good


def good_mirrors_spkg(TS, ref_spkg):
    """
    returns list of good mirrors for the spkgs
    """
    info("compiling list of good mirrors for the src/spkgs")
    good = []
    global OUTPUT
    for mirror in sorted(TS.keys(), key=lambda m: m.name):
        if len(TS[mirror]) >= 5 and TS[mirror][4] == ref_spkg:
            good.append(mirror)
            OUTPUT += '+ %s\n' % mirror.name
        else:
            OUTPUT += '- %s rejected\n' % mirror.name
    OUTPUT += '\n'
    return good


def build_mirrorselector(mirrors, TS):
    """
    builds the mirrorselector.html page, see sample at the bottom
    """
    global OUTPUT
    page = TS_INTRO
    global TOTAL_NUMBER
    #page += '(%2.0f%%)' % (float(len(mirrors))/float(TOTAL_NUMBER-1)*100.0)
    if len(mirrors) <= 5:
        page += TS_SYNC
    # if bin != src version, new release upcoming!
    if TS.values()[0][0] != TS.values()[0][1]:
        page += TS_NEW
    page += '\n<table id="mirror">\n'
    # category by name
    for c in sorted(CATEGORY.iteritems(), key=lambda x: x[1]):
        OUTPUT += c[1] + ' : '
        # per category, mirrors sorted by name (disabled!)
        # ms = [m.entry() for m in sorted(mirrors, key=lambda x: x.name) if m.cat == c[0]]
        ms = [m.entry() for m in mirrors if m.cat == c[0]]
        # shuffeling list, because the first mirror per category
        # is selected very often.
        import random
        random.shuffle(ms)
        OUTPUT += ', '.join([m.name for m in sorted(mirrors, key=lambda x: x.name) if m.cat == c[0]]) + '\n'
        if len(ms) > 0:
            page += '<tr>\n'
            page += '<td>' + c[1] + '</td><td>\n'
            page += ('<br/>\n').join(ms)
            page += '</td></tr>\n'
    page += '</table>\n'
    # global category for metalinks, then continent/server
    page += '''\
<h4>Distributed and P2P</h4>
<ul>
 <li style="font-size: 90%;">
   <a href="./mirror/torrents.html">BitTorrent</a> &mdash;
    is a P2P protocol for fast and reliable downloads of huge files
    over the Internet (<a href="http://en.wikipedia.org/wiki/BitTorrent">read more</a>).
 </li>
 <li style="font-size: 90%;">
    <a href="./mirror/metalinks.html">Metalinks</a> &mdash;
     provide fast, stable and resumeable downloads via a
     <a href="http://www.metalinker.org/samples.html">download client</a> (<a href="http://en.wikipedia.org/wiki/Metalink">read more</a>).
 </li>
</ul>
'''
    page += TS_OUTRO
    return page


def build_mirror_list(good):
    """
    mirror_list file to be parsed by a python program,
    import urllib
    eval(urllib.urlopen('http://.../mirror_list').read())
    """
    global OUTPUT
    info('building mirror_link page')
    ret = '# Sage Mirror List - %s\n' % time.asctime()
    ret += '# python usage:\n'
    ret += '# import urllib\n'
    ret += '# eval(urllib.urlopen(\'http://www.sagemath.org/mirror_list\').read())\n'
    ret += '[' + ','.join(['"%s"' % m.url for m in sorted(good, key=lambda x: x.url)]) + ']'
    OUTPUT += ret + '\n'
    return ret


def publish(good, good_spkg, TS):
    """
    publishs the page and mirror list to the website
    """
    info('building mirrorselector page')
    out = build_mirrorselector(good, TS)
    info('building mirrorselector page for src/spkg')
    out_spkg = build_mirrorselector(good_spkg, TS)
    out_list = build_mirror_list(good_spkg)
    global OUTPUT
    info('publishing')
    for t in TARGETS:
        with  open(t, 'w') as F:
            F.write(out)
        OUTPUT += 'published mirrorselector page to %s\n' % t
    for t in TARGETS_SPKG:
        with open(t, 'w') as F:
            F.write(out_spkg)
        OUTPUT += 'published mirrorselector page for src/spkg to %s\n' % t
    for t in TARGETS_LIST:
        with open(t, 'w') as F:
            F.write(out_list)
        OUTPUT += 'published mirror_list page to %s\n' % t
    with open(OUTPUT_FILE, 'w') as F:
        F.write(OUTPUT)


def metalink_helper(M):
    info("metalink helper file")
    # also includes master with prority 1, reversed(M[1:]) to avoid master completely
    out = '\n'.join([' '.join([m.country, str(m.priority), ' % ', m.url]) for m in reversed(M)])
    out += '\n'
    for MF in METALINK_FILE:
        with open(MF, 'w') as F:
            F.write(out)
    global OUTPUT
    OUTPUT += out

    info("torren helper file")
    # torrent.helper
    out = '\n'.join([m.url for m in M])
    for TF in TORRENT_FILE:
        with open(TF, "w") as F:
            F.write(out)
    OUTPUT += out

############### main program and logic ###################
# split into blocks for easier understanding and editing #

if __name__ == '__main__':
    info('Mirror Management Script started %s' % time.asctime(time.gmtime()))

    with open(MIRRORS_HTML, 'w') as MH:
        MH.write(mirrors_html())
    TS = fetch_timestamps()
    TS = extract_timestamps(TS)
    TS = dissect_timestamps(TS)
    ref, ref_spkg = find_reference(TS)
    good = good_mirrors(TS, ref)
    log(good)
    good_spkg = good_mirrors_spkg(TS, ref_spkg)
    info("list of valid mirrors")
    for m in good:
        OUTPUT += m.name + '\n'
    info("list of valid mirrors for src/spkg")
    for m in good_spkg:
        OUTPUT += m.name + '\n'
    metalink_helper(MIRRORS)
    publish(good, good_spkg, TS)
    # calling visualization
    os.system("python mirror_log_visualize.py")
