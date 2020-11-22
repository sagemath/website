#!/usr/bin/env python
"""
deletes the first line
necessary for xml output of xml.dom.ext.PrettyPrint to help
IE 6 and 7 to read the webpage in standard mode.
otherwise it falls back to the stupid quirks mode and everything is fubar
"""


def delFirstLine(fn):
    """
    deletes first line
    @fn: string of file name
    """
    with open(fn, 'r') as f:
        lines = f.readlines()
    with open(fn, 'w') as f:
        f.write('\n'.join(lines[1:]))


class UnicodeFileWriter:

    def __init__(self, file):
        self._file = file

    def write(self, data):
        self._file.write(data)
