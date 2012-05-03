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
import os.path
import datetime
  
from settings import Settings
from note import Note
from sync import Sync
#from document import Document

__author__ = 'Benoit HERVIER (Khertan)'
__email__ = 'khertan@khertan.net'
__version__ = '1.0.0'

class QmlDirReaderWriter(QObject):
   ''' A class for manipulating file and directory from Qml'''
   def __init__(self, ):
       QObject.__init__(self)
       if not os.path.exists(Note.NOTESPATH):
           try:
               os.mkdir(Note.NOTESPATH)
           except Exception,e:
               print 'Can t create note storage folder', str(e)
               
       if not os.path.exists(Note.DELETEDNOTESPATH):
           try:
               os.mkdir(Note.DELETEDNOTESPATH)
           except Exception,e:
               print 'Can t create note delete storage folder', str(e)
               
class NotesModel(QAbstractListModel):
    COLUMNS = ('title', 'timestamp', 'uuid')
 
    def __init__(self, ):
        self._notes = {}
        QAbstractListModel.__init__(self)        
        self.setRoleNames(dict(enumerate(NotesModel.COLUMNS)))
        self.loadData()
         
    def loadData(self,):
        self._notes = [Note(uid=file) for file in os.listdir(Note.NOTESPATH) if os.path.isfile(os.path.join(Note.NOTESPATH,file))]                
        self._notes.sort(key=lambda note: note.timestamp, reverse=True)
            
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

    @Slot()
    def reload(self):
        print 'reload'
        self.loadData()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(
                                                       len(self._notes), len(NotesModel.COLUMNS)))
            
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
        self.notesController = NotesControler()
        self.notesModel = NotesModel()
        self.note = Note()
        self.syncer = Sync()
        self.rootContext = self.view.rootContext()
        self.rootContext.setContextProperty("argv", sys.argv)
        self.rootContext.setContextProperty("__version__", __version__)
        self.rootContext.setContextProperty("Settings", Settings())
        self.rootContext.setContextProperty("Sync", self.syncer)
        self.rootContext.setContextProperty("QmlDirReaderWriter", QmlDirReaderWriter())
        self.rootContext.setContextProperty('notesController', self.notesController)
        self.rootContext.setContextProperty('notesModel', self.notesModel)
        self.rootContext.setContextProperty('Note',self.note)
        self.view.setSource(QUrl.fromLocalFile(
                os.path.join(os.path.dirname(__file__), 'qml',  'main.qml')))
        self.rootObject = self.view.rootObject()
        self.note.on_error.connect(self.rootObject.onError)
        self.syncer.on_error.connect(self.rootObject.onError)
        self.view.showFullScreen()

if __name__ == '__main__':
    sys.exit(KhtNotes().exec_())                      
