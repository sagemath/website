#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this script visualizes the mirror management logfile
# author: harald schilly <harald.schilly@gmail.com>
# license: apache 2.0

import Image
import ImageDraw
import ImageFont
import colorsys
import time
import math
import csv
import os
import sys
from random import randint as rint
import random
import urllib2
#from random import randint as rint

# script uses relative paths, switch to its
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

ts = time.strftime('%Y-%U', time.gmtime())  # Year-Week
# if timestamp is given, use it instead
if len(sys.argv) > 1:
    ts = sys.argv[1]
dir = './mirror-log/'
file = dir + 'mirror_manager_%s.log' % ts
output = dir + 'mirror_manager_%s.png' % ts
#website = urllib2.urlopen('http://sage.math.washington.edu/home/schilly/mm/mirror_manager.log')
website = open(file)
content = list(csv.reader(website, delimiter=';'))
length = len(content) + 10
line_width = 340
off_sum = line_width + 35
off_txt = off_sum + 50  # offset text on the right

random.seed(29)
black = (0, 0, 0)
grey1 = (50, 50, 50)
grey2 = (120, 120, 120)
grey3 = (200, 200, 200)
grey = lambda c, x: ((c - x) % 255, (c - x) % 255, (c - x) % 255)

if len(sys.argv) == 1:  # no logfile given
    symlink = dir + 'mirror_manager.png'
    if os.path.exists(symlink):
        os.remove(symlink)
    os.symlink('./mirror_manager_%s.png' % ts, symlink)

img = Image.new("RGB", (800, max(length, 600)), "#FFFFFF")
draw = ImageDraw.Draw(img)
f = ImageFont.load_default()
#f = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono.ttf", 8)

# holds position data and statistics
# key=servername=entry
pos = dict()

ts = time.strptime(content[0][0].replace(' ', ''), '%Y%m%d-%H:%M:%S')
last_hour = ts[3]
last_day = ts[2]
for i, data in enumerate(content):
    i = length - i  # + 10
    ts = time.strptime(data[0].replace(' ', ''), '%Y%m%d-%H:%M:%S')
    if last_hour != ts[3]:
        last_hour = ts[3]
        draw.line((0, i, line_width - 20, i), fill=grey3)
        if last_hour % 4 == 0:
            draw.text((line_width - 2, i - 5), '%2d' % last_hour, font=f, fill=grey2)
        if ts[2] != last_day:
            last_day = ts[2]
            draw.line((0, i, line_width, i), fill=grey2)
            draw.text((line_width - 12, i + 1), str(ts[2] - 1), font=f, fill=grey2)
            draw.text((line_width - 12, i - 11), str(ts[2]), font=f, fill=grey2)

#    if not str(ts[4])[-1] == '0' or str(ts[4])[-1] == '1':
#        continue
    # print data
    for s in data[1:-1]:
        offset = 0
        if s in pos:
            offset, color, cnt = pos.get(s)
            pos[s] = ((offset, color, cnt + 1))
        else:
            offset = 9 * len(pos.keys())
            # rainbow
            # color = tuple(map(int, colorsys.hsv_to_rgb(float(offset)/200,0.7,160)))
            # color = (rint(10,180), rint(10,180), rint(10,180))
            color = (hash(s[0:len(s) - 3]) % 150 + 10, hash(s[1:len(s) - 2]) % 150 + 10, hash(s[2:len(s) - 1]) % 150 + 10)
            pos[s] = (offset, (color), 1)
        draw.line((offset, i, offset + 7, i), fill=color)
    # sum
    sum = len(data[1:-1]) / 2
    draw.line((off_sum - sum, i, off_sum + sum, i), fill=grey(150, sum * 5))

# draw online ones
for s in content[-1][1:-1]:
    offset, color, cnt = pos.get(s)
    draw.rectangle((offset, 0, offset + 7, 7), fill=color)

# print mirrors
draw.text((off_txt - 20, 0), time.strftime('Sage Mirrors (%Y/week %U)', time.gmtime()), font=f, fill=black)
length = len(content)  # redefined
for key, value in pos.iteritems():
    p = 100 * float(value[2]) / length
    txt = '%5.1f%% %s' % (p, key)
    draw.rectangle((off_txt - math.floor(p / 5) - 4, 21 + value[0], off_txt - 3, 29 + value[0]), fill=value[1])
    draw.text((off_txt, 20 + value[0]), txt, font=f, fill=value[1])

# info
off = len(pos) * 10 + 20
draw.text((off_txt, off + 20), 'Start:', font=f, fill=(0, 0, 0))
draw.text((off_txt, off + 30), content[0][0], font=f, fill=(0, 0, 0))
draw.text((off_txt, off + 40), 'End:', font=f, fill=(0, 0, 0))
draw.text((off_txt, off + 50), content[-1][0], font=f, fill=(0, 0, 0))

img.save(output, "PNG")
