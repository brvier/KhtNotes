#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Benoit HERVIER <khertan@khertan.net>
# Licenced under GPLv3

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 3 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

from PySide.QtGui import QApplication
from PySide.QtCore import QUrl, Slot, QObject, Property, Signal
from PySide import QtDeclarative

import threading
import sys
import os
import markdown2
import re
  
class Document(QObject):
   '''Represent the text document'''

   def __init__(self,):
       QObject.__init__(self,)
       self._text = u''
       self._modified = False
       self._filepath = u''
       self._ready = False

   @Slot(unicode)
   def load(self,path):
       ''' Load the document from a path in a thread'''
       self._set_ready(False)
       self.thread = threading.Thread(target=self._load, args= (path, ))
       self.thread.start()


   def _load(self,path):
        ''' Load the document from a path '''
        self.filepath = QUrl(path).path()
        try:
          with open(self.filepath, 'rb') as fh:
            try:
                self._set_text(unicode(fh.read(), 'utf-8'))
                self._set_ready(True)
            except Exception, e:
                print e
                self.on_error.emit(str(e))
                self._set_ready(True)
        except:
          self._text = u''
          self._set_ready(True)

   @Slot(unicode, result=unicode)
   def previewMarkdown(self, text):
       ''' Generate a markdown preview'''
       try:
           return markdown2.markdown(self._stripTags(text))
       except:
           return text

   @Slot(unicode)
   def write(self, data):
       ''' Write the document to a file '''
       try:
           with open(self.filepath, 'wb') as fh:
               fh.write(data.encode('utf-8'))
       except Exception, e:
           print e
           self.on_error.emit(str(e))

   def _get_text(self):
       return self._text
   def _set_text(self, text):
       self._text = text
       self.on_text.emit()

   def _get_ready(self):
       return self._ready
   def _set_ready(self, b):
       self._ready = b
       self.on_ready.emit()
             
   on_text = Signal()
   on_error = Signal(unicode)
   on_ready = Signal()
   text = Property(unicode, _get_text, _set_text, notify=on_text)
   ready = Property(bool, _get_ready, _set_ready, notify=on_ready)