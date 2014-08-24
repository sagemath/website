#!/usr/bin/env python
# coding: utf8
# continuous build based on pyInotify
#
# To avoid excessive re-runs and calling make twice concurrently (bad idea!),
# there is a little process-based contraption built around this.
# do_compilation is an "Event", which can be set and triggers the compilation.
# If there is a re-trigger during compilation, that's not a problem.
# Also, a bunch of triggers are coalesced together (see time.sleep below)
#
# tl;dr: visualization of the mechanism: http://youtu.be/Z86V_ICUCD4

import subprocess
import multiprocessing as mp
import sys
import pyinotify
IN_MODIFY = pyinotify.IN_MODIFY
IN_CREATE = pyinotify.IN_CREATE
IN_DELETE = pyinotify.IN_DELETE
from os.path import exists, abspath
import time

do_compilation = mp.Event()
do_compilation.set()  # run it once after startup


def compile_it(cmd="make"):
    """
    This is executed on demand in a proper sub-process.

    :param cmd:
    :return:
    """
    try:
        while True:
            do_compilation.wait()
            # wait a bit in case multiple events fire
            time.sleep(0.1)
            do_compilation.clear()
            print("==> running '%s'" % cmd)
            subprocess.Popen(cmd, shell=True,
                             stdout=sys.stdout, stderr=sys.stderr)
    except KeyboardInterrupt:
        pass


class OnWriteHandler(pyinotify.ProcessEvent):

    def my_init(self, cmd):
        self.cmd = cmd

    def process_IN_MODIFY(self, event):
        do_compilation.set()

    def process_IN_CREATE(self, event):
        do_compilation.set()

    def process_IN_DELETE(self, event):
        do_compilation.set()


def autocompile(paths, cmd):
    wm = pyinotify.WatchManager()
    handler = OnWriteHandler(cmd=cmd)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(paths,
                 # pyinotify.ALL_EVENTS,
                 #IN_CREATE | IN_MODIFY | IN_DELETE,
                 IN_MODIFY,  # but still all?!
                 rec=True,
                 auto_add=True)
    print '==> Start monitoring %s (type CTRL-c to exit)' % paths
    notifier.loop()

if __name__ == '__main__':
    paths = ["src", "conf", "templates", "scripts"]
    cmd = 'make'

    compilation_process = mp.Process(target=compile_it, args=(cmd,))
    compilation_process.start()

    # Blocks monitoring
    try:
        autocompile(paths, cmd)
    finally:
        compilation_process.terminate()
