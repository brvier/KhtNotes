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
from PySide.QtCore import QUrl, Slot, QObject, Property, Signal, QAbstractListModel, QModelIndex
from PySide import QtDeclarative
from PySide.QtOpenGL import QGLWidget

import sys
import os
import datetime
import uuid
import markdown2

class Note(QObject):
    ''' A class representing a note '''

    NOTESPATH = os.path.expanduser('~/.khtnotes')
    DELETEDNOTESPATH = os.path.expanduser('~/.khtnotes/deleted')

    def __init__(self, uid=None):
        QObject.__init__(self)
        self._title = u'Untitled'
        self._data = u''
        self._uuid = uid
        self._timestamp = None
        self._ready = False
        self._human_timestamp = ''
        print 'INIT:', uid
        if uid!=None:
            self._uuid = uid
            self.load()

    @Slot(unicode)
    def write(self, data):
       ''' Write the document to a file '''
       print 'write:', self._uuid
       path = os.path.join(self.NOTESPATH, self._uuid)             
       try:
           with open(path, 'wb') as fh:
               fh.write(data.encode('utf-8'))
               self._set_timestamp(os.stat(path).st_mtime)
               self._set_title(self._data.split('\n', 1)[0])
               self.onDataChanged.emit()
               print path , ' written'
       except Exception, e:
           print e
           self.on_error.emit(str(e))

    @Slot(unicode)
    def rm(self, uuid = None):
        if uuid != None:
            self._uuid = uuid
        try:
            if not os.path.exists(self.DELETEDNOTESPATH):
               os.mkdir(self.DELETEDNOTESPATH)
            os.rename(os.path.join(self.NOTESPATH, self._uuid), os.path.join(self.DELETEDNOTESPATH, self._uuid))
        except Exception, e:
            self.on_error.emit(str(e))
            
    def overwrite_timestamp(self, timestamp):
        print type(timestamp), timestamp
        if type(timestamp) == unicode:
            if len(timestamp) <= 14:
                timestamp = '%s.%s' % (timestamp[:9] , timestamp[10:]) 
            timestamp = float(timestamp)
        os.utime(os.path.join(self.NOTESPATH, self._uuid), (timestamp, timestamp))
        
    @Slot(unicode)        
    def load(self, uid=None):
        auid = self._uuid
        if uid:
          if (uid != ''):
            self._set_uuid(uid)

        if (uid == 'new'):
            self._set_uuid(unicode(uuid.uuid4().int))
            self._set_title('')
            self._set_text('')
            self._set_ready(True) 
        if (self._uuid ==None):
            print 'LOAD:', self._uuid
            self._set_uuid(unicode(uuid.uuid4().int)) 	    
        
        if (self._uuid != None):
            try:
                path = os.path.join(self.NOTESPATH, str(self._uuid))                
                print 'path: ', path
                with open(path, 'rb') as fh:
                    try:
                        self._set_text(unicode(fh.read(), 'utf-8'))
                        print self._data
                        if self._data == '':
                          self._set_timestamp(0)
                          self._set_title('')
                        else:
                          self._set_timestamp(os.stat(path).st_mtime)
                          self._set_title(self._data.split('\n', 1)[0])
                        self._set_ready(True)
                    except Exception, e:
                        print e
                        self.on_error.emit(str(e))
                        self._set_ready(True)
            except Exception, e:
                print e

    @Slot(unicode, result=unicode)
    def previewMarkdown(self, text):
        ''' Generate a markdown preview'''
        try:
           return markdown2.markdown(self._stripTags(text))
        except:
           return text
           
    def _get_text(self):
        return self._data
    def _set_text(self, text):
        self._data = text
        self.onDataChanged.emit()

    def _get_title(self):
        return self._title
    def _set_title(self, title):
        self._title = title
        self.onTitleChanged.emit()

    def _get_uuid(self):
        return self._uuid
    def _set_uuid(self, uuid):
        self._uuid = unicode(uuid)
        self.onUuidChanged.emit()

    def _get_timestamp(self):
        return self._timestamp
    def _set_timestamp(self, timestamp):
        self._timestamp = timestamp
	self._human_timestamp = datetime.datetime.fromtimestamp(self._timestamp).strftime('%x %X')
        self.onTimestampChanged.emit()
        self.onHumanTimestampChanged.emit()
        
    def _get_ready(self):
        return self._ready
    def _set_ready(self, b):
        self._ready = b
        self.onReadyChanged.emit()
             
    def _get_human_timestamp(self):
    	return self._human_timestamp
    	
    onDataChanged = Signal()
    onTitleChanged = Signal()
    onUuidChanged = Signal()
    onTimestampChanged = Signal()
    on_error = Signal(unicode)
    onReadyChanged = Signal()    
    onHumanTimestampChanged = Signal()
    human_timestamp = Property(unicode, _get_human_timestamp, notify=onHumanTimestampChanged)
    data = Property(unicode, _get_text, _set_text, notify=onDataChanged)
    title = Property(unicode, _get_title, _set_title, notify=onTitleChanged)
    uuid = Property(unicode, _get_uuid, _set_uuid, notify=onUuidChanged)
    timestamp = Property(int, _get_timestamp, _set_timestamp, notify=onTimestampChanged)
    ready = Property(bool, _get_ready, _set_ready, notify=onReadyChanged)
   
