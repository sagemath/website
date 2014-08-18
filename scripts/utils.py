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
   f = open( fn, 'r' )
   lines = f.readlines()
   f.close()
   
   f = open( fn, 'w' )
   f.write( '\n'.join( lines[1:] ) )
   f.close()



class UnicodeFileWriter:
    def __init__(self, file):
	self._file = file
    def write(self, data):
        self._file.write(data.encode('utf-8'))

