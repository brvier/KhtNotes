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
  
from settings import Settings
from document import Document

__author__ = 'Benoit HERVIER (Khertan)'
__email__ = 'khertan@khertan.net'
__version__ = '0.0.1'

NOTESPATH = os.path.expanduser('~/.khtnotes')

class QmlDirReaderWriter(QObject):
   ''' A class for manipulating file and directory from Qml'''
   def __init__(self, ):
       QObject.__init__(self)
       if not os.path.exists(NOTESPATH):
           try:
               os.mkdir(NOTESPATH)
           except Exception,e:
               print 'Can t create note storage folder', str(e)
               
class Note(QObject):
    ''' A class representing a note '''
    def __init__(self, uuid=None):
        QObject.__init__(self)
        self._title = u'Untitled'
        self._data = u''
        self._uuid = uuid
        self._timestamp = None
        self._ready = False
	self._human_timestamp = ''
        if self.uuid != None:
            self.load()
            
    @Slot(int)        
    def load(self, an_uuid= None):
	if an_uuid != None:
	    self._uuid = an_uuid
        if (self._uuid != None):
            try:
                path = os.path.join(NOTESPATH, str(self._uuid))                
                print 'path: ', path
                with open(path, 'rb') as fh:
                    try:
                        self._set_text(unicode(fh.read(), 'utf-8'))
                        print self._data
                        self._set_timestamp(os.stat(path).st_mtime)
                        self._set_title(self._data.split('\n', 1)[0])
                        self._set_ready(True)
                    except Exception, e:
                        print e
                        self.on_error.emit(str(e))
                        self._set_ready(True)
            except Exception, e:
                print e
                
    def _get_text(self):
        return self._data
    def _set_text(self, text):
        self._data = text
        self.on_data.emit()

    def _get_title(self):
        return self._title
    def _set_title(self, title):
        self._title = title
        self.on_title.emit()

    def _get_uuid(self):
        return self._uuid
    def _set_uuid(self, uuid):
        self._uuid = uuid
        self.on_uuid.emit()

    def _get_timestamp(self):
        return self._timestamp
    def _set_timestamp(self, timestamp):
        self._timestamp = timestamp
	self._human_timestamp = datetime.datetime.fromtimestamp(self._timestamp).strftime('%x %X')
        self.on_timestamp.emit()
        self.on_human_timestamp.emit()
        
    def _get_ready(self):
        return self._ready
    def _set_ready(self, b):
        self._ready = b
        self.on_ready.emit()
             
    def _get_human_timestamp(self):
    	return self._human_timestamp
    	
    on_data = Signal()
    on_title = Signal()
    on_uuid = Signal()
    on_timestamp = Signal()
    on_error = Signal(unicode)
    on_ready = Signal()    
    on_human_timestamp = Signal()
    human_timestamp = Property(unicode, _get_human_timestamp, notify=on_human_timestamp)
    data = Property(unicode, _get_text, _set_text, notify=on_data)
    title = Property(unicode, _get_title, _set_title, notify=on_title)
    uuid = Property(unicode, _get_uuid, _set_uuid, notify=on_uuid)
    timestamp = Property(int, _get_timestamp, _set_timestamp, notify=on_timestamp)
    ready = Property(bool, _get_ready, _set_ready, notify=on_ready)
   
class NotesModel(QAbstractListModel):
    COLUMNS = ('title', 'timestamp', 'uuid')
 
    def __init__(self, ):
        self._notes = {}
        QAbstractListModel.__init__(self)        
        self.setRoleNames(dict(enumerate(NotesModel.COLUMNS)))
        self.loadData()
         
    def loadData(self,):
        path = os.path.expanduser('~/.khtnotes/')
        for root, dirs, files in os.walk(path):
            self._notes =  [Note(uuid=file) for file in files]                
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._notes)
 
    def data(self, index, role):
        if index.isValid() and role == NotesModel.COLUMNS.index('title'):
            return self._notes[index.row()].title
        if index.isValid() and role == NotesModel.COLUMNS.index('timestamp'):
            return self._notes[index.row()].human_timestamp
        if index.isValid() and role == NotesModel.COLUMNS.index('uuid'):
            return self._notes[index.row()].uuid
        return None
        
class NotesControler(QObject):
    @Slot(QObject)
    def noteSelected(self, wrapper):
        print 'User clicked on:', wrapper._notes.title, ' uuid : ', wrapper._notes.uuid

        
class KhtNotes(QApplication):
    ''' Application class '''
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        self.setOrganizationName("Khertan Software")
        self.setOrganizationDomain("khertan.net")
        self.setApplicationName("KhtNotes")

        self.view = QtDeclarative.QDeclarativeView()
        self.glw = QGLWidget()
        self.view.setViewport(self.glw)
        self.aDocument = Document() 
        self.notesController = NotesControler()
        self.notesModel = NotesModel()
        self.note = Note()
        self.rootContext = self.view.rootContext()
        self.rootContext.setContextProperty("argv", sys.argv)
        self.rootContext.setContextProperty("__version__", __version__)
        self.rootContext.setContextProperty("Settings", Settings())
        self.rootContext.setContextProperty("QmlDirReaderWriter", QmlDirReaderWriter())
        self.rootContext.setContextProperty('Document', self.aDocument)
        self.rootContext.setContextProperty('notesController', self.notesController)
        self.rootContext.setContextProperty('notesModel', self.notesModel)
        self.rootContext.setContextProperty('Note',self.note)
        self.view.setSource(QUrl.fromLocalFile(
                os.path.join(os.path.dirname(__file__), 'qml',  'main.qml')))
        self.rootObject = self.view.rootObject()
        self.aDocument.on_error.connect(self.rootObject.onError)
        self.view.showFullScreen()

if __name__ == '__main__':
    sys.exit(KhtNotes().exec_())                  