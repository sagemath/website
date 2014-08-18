#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
This file parses the boxen specific apache logfiles for www_sagemath_org
It generates a statistic for all SPKGes, which are not standard and
writes out a website for them. The same for the documentation files in
/doc/*, where it also splits the statistic apart for each chapter (and
for 'reference', also one level deeper).

The logfiles are expected to be uncompressed text and rotated via logrotate
on a daily basis. e.g. <filename>.<epoch long timestamp>.

It also has a persistant storage for the statistical data in a *.dump file,
where it stores the current state. The analyzer function only parses those
lines, where the timestamp is larger than the last one it has seen in the 
previous run (note, that this means that lines with exactly the same timestamp
are skipped … likely only a few or none. granularity of timestamp is seconds.)

The dump is compressed via lzma in a os.system call.

Note, this file is intended to be run ~hourly via crontab.
"""
from __future__ import with_statement
import re
import sys, os
from glob import glob
from datetime import datetime
from itertools import groupby
from math import log
from cPickle import load, dump

#script uses relative paths, switch to its
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# output files
spkg_out_fn = os.path.join(os.path.curdir, 'www', 'spkg_stats.html')
doc_out_fn  = os.path.join(os.path.curdir, 'www', 'doc_stats.html')
data_fn     = os.path.join(os.path.curdir, 'apache_stats.dump')

spkg_line = re.compile(r'.*"GET /.*\.spkg .*')
doc_line = re.compile(r'.*"GET /doc/.*')
log_line = re.compile(r'(?P<host>\S+) - - \[(?P<time>.+)\] "(?P<request>.+)" (?P<status>\d+) .*')

# logfiles are parsed one by one, start/end for spkg output stores (year, month) tuples
class Data(object):
  '''this is the state that's serialized into the dump file'''
  def __init__(self):
    self.spkg_stats = {}
    self.doc_stats = {}
    self.spkg_cat = {} # maps spkg name to its category (optional, huge, …)
    self.spkg_uip = set() # unique IPs
    self.doc_uip = set() # unique IPs
    self.start, self.end = (9999,99), (0,0) # start and end of (year, month)
    self.ts_first, self.ts_last = datetime.fromtimestamp(2**32), datetime.fromtimestamp(0) # first and last timestamp

# used for reading the apache logfile timestamp
month_map = dict([(k, i+1) for i,k in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])])
month_map_inv = dict((v, k) for k, v in month_map.iteritems())

# grayscale map, should be 99 to FF in hex
grays = [ hex(_)[2:4] for _  in range(0x99,0xFF+1)][::-1]

def apachetime(s):
    "e.g. '28/Jun/2013:00:47:13 -0700' => datetime"
    return datetime(int(s[7:11]), month_map[s[3:6]], int(s[0:2]), \
         int(s[12:14]), int(s[15:17]), int(s[18:20]))

def analyze(logfile):
  print 'scanning', logfile

  for line_no, line in enumerate(file(logfile, 'r')):
    # check if there is a newer line (newer than in the Data (data_fn) dump)
    res = log_line.match(line)
    if res is None: continue
    res = res.groupdict()
    ltime = apachetime(res['time'])
    if line_no == 0: ltime_first = ltime
    if ltime < db.ts_last: continue # skip old data
    #print 'new:', line
    # otherwise update timestamps
    if res['status'] != "200": continue

    # SPKG request (/packages/, /spkg/, /mirror/, ... ?)
    if spkg_line.match(line):
       db.spkg_uip.add(res['host'])
       path = res['request'].split(" ")[1]
       yearmonth = ltime.year, ltime.month
       #print path
       cat, spkg = path.split("/")[-2:]
       #print cat, spkg
       if cat != 'standard':
         k = (yearmonth, spkg) # key of a sparse 2d matrix
         db.spkg_stats[k] = db.spkg_stats.get(k, 0) + 1
         db.spkg_cat[spkg] = cat # category
         if   yearmonth < db.start: db.start = yearmonth
         elif yearmonth > db.end:   db.end = yearmonth

    # documentation file, prefix '/doc/'
    elif doc_line.match(line):
       db.doc_uip.add(res['host'])
       path = res['request'].split(" ")[1]
       #print path
       path = path[4:]
       #print cat, spkg
       if path.endswith('.html'):
         db.doc_stats[path] = db.doc_stats.get(path, 0) + 1

  # update the first & last time info, AFTER the for loop!
  # that's necessary, because timestamps are only in seconds and consecutive entries are ignored
  # ltime is automatically the last one!
  if db.ts_first is None or db.ts_first > ltime_first: db.ts_first = ltime_first
  if db.ts_last  is None or db.ts_last  < ltime:       db.ts_last  = ltime

def output_spkg():
  # used for the grayscale highlighting
  maxval = max(db.spkg_stats.values())
  scale = (len(grays)-1) / float(maxval)

  def cat_color(c):
    if   c == 'archive' :      return '#fbc'
    elif c == 'experimental' : return '#dfc'
    elif c == 'optional':      return '#cdf'
    elif c == 'sagedb':        return '#baf'
    # otherwise make one up:
    ccc = [ (hash(c[i:3-i]) % 97) for i in range(3) ]
    ccc = [ _ + (240 - max(ccc)) for _  in ccc ]
    ccc = [ hex(_)[-2:] for _ in ccc ]
    return '#%s' % ''.join(ccc)

  def ym(yearmonth):
    y, m = yearmonth
    return "%s'%s" % (month_map_inv[m], str(y)[-2:])

  def timespan():
    """
    iterator for the previous time direction, 
    e.g. (2013,1) => (2012, 12)
    """
    t = db.end
    while t >= db.start:
      yield t
      if t[1] > 1:
        t = t[0], t[1] - 1
      else:
        t = t[0] - 1, 12

  def thead(f):
    f.write("<thead><tr><td></td><td></td>")
    for t in timespan():
      f.write("<th>%s</th>" % ym(t))
    f.write("</tr></thead>")

  def thead_stats(f):
    f.write("<tr><td></td><th>&Sigma;</th>")
    sums = [ sum(v for _, v in 
             filter(lambda _:_[0][0] == t, db.spkg_stats.iteritems()))
             for t in timespan() ]
    scale = (len(grays)-1) / float(max(sums))
    for s in sums:
      ccc = grays[int(scale * s)] * 3
      f.write("<td style='background:#%s'>%s</td>" % (ccc, s))

  def trow(f, spkg, rowsum):
    ccc = grays[ int(rowsum_scale * rowsum) ] * 3
    f.write("<td style='background:#%s'>%s</td>" % (ccc, rowsum))
    for t in timespan():
      v = db.spkg_stats.get((t, spkg), 0)
      if v != 0:
        ccc = grays[ int(scale * v) ] * 3
      else:
        ccc = ''
      f.write("<td style='background: #%s;'>%s</td>" % (ccc, v))

  names = sorted(set([ _[1] for _ in db.spkg_stats.keys()]), key = lambda _ : _.lower())
  cats = sorted(set(db.spkg_cat.values()))
  with open(spkg_out_fn, 'w') as f:
    f.write('''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=300px, initial-scale=1.0">
<title>SPKG Statistics</title>
<style>
html { font-family: sans-serif; font-size: 11px; }
table {  border-collapse: collapse; border-spacing: 0; 
         padding: 20px; border: 1px solid gray; font-size: inherit;}
table td, table th { border: 1px solid gray; width: 40px; white-space: nowrap; }
table tbody th { text-align: left; }
table tbody td { text-align: right; }
</style>
</head>
<body>\n''')
    f.write('<h1><a href="http://www.sagemath.org/links-components.html">SPKG</a> Statistics</h1>') 
    cat_list = ', '.join('<span style="background:%s;">%s</span>' % (cat_color(_), _) for _ in cats)
    f.write('<div>Categories: %s</div>' % cat_list)
    ts_diff = db.ts_last - db.ts_first
    r = '%d days and %.1f hours' % (ts_diff.days, ts_diff.seconds / 60 / 60.)
    f.write('<div>Data spans %s to %s (%s)</div>' % (db.ts_first, db.ts_last, r))
    perday = float(ts_diff.seconds + ts_diff.days * 60 * 60 * 24) / (60*60*24)
    nbuip = len(db.spkg_uip)
    nbuippd = nbuip / perday
    totdl = sum(db.spkg_stats.values())
    totdlpd = totdl / perday
    f.write('<div>Total number of downlods: %d (= %.2f / day)</div>' % (totdl, totdlpd))
    f.write('<div>Number of unique IPs: %d (= %.2f / day)</div>' % (nbuip, nbuippd))
    f.write('<table>\n')
    thead(f)
    thead_stats(f)
    # sort by popularity, then by name

    rowsums = [ sum(v for _, v in
                filter(lambda _:_[0][1] == spkg, db.spkg_stats.iteritems()))
                for spkg in names ]
    rowsum_scale = (len(grays) - 1) / float(max(rowsums))
    for spkg, rowsum in zip(names, rowsums):
      f.write('<tr><th style="background: %s">%s</th>\n' % (cat_color(db.spkg_cat[spkg]), spkg[:-5]))
      trow(f, spkg, rowsum)
      f.write('</tr>\n')
    f.write('</table>')
    f.write('\n\ngenerated: %s UTC' % datetime.utcnow())
    

def output_doc(th = 3, limit = 15):
  # used for the grayscale highlighting
  maxval = max(db.doc_stats.values())
  scale = len(grays) / float(maxval)
  log_scale = (len(grays) - 1) / log(len(grays))

  def category(entry):
    'extracts the title for the table, special case "reference" goes one level deeper'
    path = entry[0].split("/")
    if len(path) == 2: return '/'
    if len(path) > 3:
      if path[1] == 'reference':
        return '/'.join(path[1:3])
    return path[1]


  def toc(grouped):
    f.write("<h2><a name='TOC'>TOC</a></h2>\n")
    f.write("<div>")
    f.write(' &middot;\n '.join(('<a href="#%s">%s</a>' % (k ,k.title())) for k, _ in grouped))
    f.write("</div>")
  
  def write_table(title, entries):
    tbl = ''
    total = 0

    # sort by popularity
    for idx, k in enumerate(sorted(entries, key = lambda _ : -_[1])):
      if idx > limit: break 
      path, freq = k
      total += freq
      if freq < th: continue # don't break b/c of total
      tokens = path.split("/")
      #path_short = '/'.join(tokens[(-1 if len(tokens) <= 3 else -2):])[:-5]
      path_short = tokens[-1][:-5]
      url = '<a href="http://sagemath.org/doc%s">%s</a>' % (path, path_short)
      c = grays[ int(log(1 + scale * freq) * log_scale) ]
      ccc = c * 3
      tbl += '<tr style="background: #%s"><td>%s</td><td>%s</td>\n' % (ccc, freq, url)

    # only render table, if there is something to report!
    if len(tbl) > 0:
      f.write('<div class="cont">')
      ttl = '<a name="%s">%s</a> (%d) <a href="#TOC">&uArr;</a>\n'\
             % (title, title.title(), total)
      f.write('<table>\n')
      f.write('<thead><tr><th>#</th><th>%s</th></tr></thead>\n<tbody>' % ttl)
      f.write(tbl)
      f.write('</tbody></table>\n')
      f.write("</div>")

  # only list files above the threshold th
  with open(doc_out_fn, 'w') as f:
    f.write('''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=300px, initial-scale=1.0">
<title>Sage Documentation Pages Statistics</title>
<style>
html { font-family: sans-serif; font-size: 11px; }
table {  border-collapse: collapse; border-spacing: 0;
         border: 1px solid gray; font-size: inherit;}
table td { border: 0; }
table thead tr { border: 1px solid gray; }
table td:first-child,
table th:first-child { text-align: right; padding-right: 5px; }
a { text-decoration: none; }
table tbody a { display: block; }
table tbody a:hover { background: #888; color: white; }
div.cont { min-height: %dpx; float: left; margin: 5px;}
@media screen and (max-width: 500px){
div.cont { min-height: 0; float: none; margin: 5px;}
}
</style>
</head>
<body>\n''' % ((1+limit) * 18 + 10)) # table height is set dynamically for the flow layout

    d = 'http://www.sagemath.org/doc/'
    f.write('<h1>Statistics for <a href="%s">Sage Documentation</a> .html files</h1>\n'%d)
    f.write("""<div>Note: for each category, the top %s above a threshold of %s
       are shown. The "Reference" category is split apart one level deeper.
       The number in brackets is the sum of all in that category.</div>"""\
        % (limit, th))
    ts_diff = db.ts_last - db.ts_first
    r = '%d days and %.1f hours' % (ts_diff.days, ts_diff.seconds / 60 / 60.)
    f.write('<div>Data spans %s to %s (%s)</div>' % (db.ts_first, db.ts_last, r))
    nbuip = len(db.doc_uip)
    perday = float(ts_diff.seconds + ts_diff.days * 60 * 60 * 24) / (60*60*24)
    nbuippd = nbuip / perday
    totpv = sum(db.doc_stats.values())
    totpvpd = totpv / perday
    f.write('<div>Number of total Pageviews: %d (= %.2f / day)</div>' % (totpv, totpvpd))
    f.write('<div>Number of unique IPs: %d (= %.2f / day)</div>' % (nbuip, nbuippd))
    data = [ (k, v) for k, v in db.doc_stats.iteritems() ]
    data = sorted(data, key = category) 
    toc(groupby(data, category))
    map(lambda _ : write_table(*_), groupby(data, category))
    f.write('<div style="clear:both;">generated: %s UTC</div>' % datetime.utcnow())

if __name__ == "__main__":
  # logfiles on boxen, they are logrotated as text only files with a timestamp in the end
  # sorted is important for skipping!
  logfiles = sorted(glob("/var/log/apache2/www_sagemath_org*"))
  global db 
  if os.path.exists(data_fn + '.lzma'):
    #update mode
    # only last two logfiles (max 2 days) for updates
    logfiles = logfiles[-2:]
    # d: decompr, k: keep (in case there is an exception, no data is lost)
    os.system('lzma -k -d %s.lzma' % data_fn)
    db = load(file(data_fn))
  else:
    db = Data()
  map(analyze, sorted(logfiles)) # sorted because of the timestamp in the name!
  output_spkg()
  output_doc()
  # serialize Data in db
  dump(db, file(data_fn, 'w'))
  os.system('rm -f %s.lzma' % data_fn) # removes the kept file
  os.system('lzma -z %s' % data_fn)
  # publishing on actual website if everything goes well
  os.system(os.path.curdir + '/go_live.sh')

