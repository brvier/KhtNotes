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
from PySide.QtCore import QUrl, Slot, QObject, \
                          QAbstractListModel, QModelIndex
from PySide import QtDeclarative
from PySide.QtOpenGL import QGLWidget

import sys
import os
import os.path

from settings import Settings
from note import Note
from sync import Sync
from importer import TomboyImporter

__author__ = 'Benoit HERVIER (Khertan)'
__email__ = 'khertan@khertan.net'
__version__ = '2.2'
__upgrade__ = '''1.1: First public release
1.2: Fix deletion of remote file in sync, add word wrapping in markdown preview
1.3: Fix a nasty bug where a new note can sometime overwrite an existing bug
1.4: Better use of harmattan invoker
1.5: Avoid double loading of initial list on startup, fix wrong logger call
     in sync, optimization of startup time And add a search feature
1.6: Add Tomboy/Conboy import feature
1.7: Improve unicode support (utf-8 and utf-16)
1.8: fix authFailure wrong import in sync
1.9: fix sync and improve delta sync diff
1.10: Fix creation of KhtNotes folder on webdav and avoid lose of notes in case of notes if path is created, improve sync and fix bugs on conflicting update
2.0: Formatted notes when markdown syntax is used
2.1: Fix the formatting of notes
2.2: Fix a bug in sync when a file conflict happen'''


class QmlDirReaderWriter(QObject):
    ''' A class for manipulating file and directory from Qml'''
    def __init__(self, ):
        QObject.__init__(self)
        if not os.path.exists(Note.NOTESPATH):
            try:
                os.mkdir(Note.NOTESPATH)
            except Exception, e:
                print 'Can t create note storage folder', str(e)


class NotesModel(QAbstractListModel):
    COLUMNS = ('title', 'timestamp', 'uuid', 'index', 'note')

    def __init__(self, ):
        self._notes = {}
        QAbstractListModel.__init__(self)
        self.setRoleNames(dict(enumerate(NotesModel.COLUMNS)))
        self._filter = None
        self._filteredNotes = self._notes

        if not os.path.exists(Note.NOTESPATH):
            try:
                os.mkdir(Note.NOTESPATH)
            except Exception, e:
                print 'Can t create note storage folder', str(e)

        #self.loadData()

    @Slot(unicode)
    def setFilterFixedString(self, search):
        self._filter = search
        self.beginResetModel()
        self._filterNotes()
        self.endResetModel()

    def _filterNotes(self):
        if self._filter:
            self._filteredNotes = [note for note in self._notes \
                                   if self._filter.lower() \
                                   in note.title.lower()]
        else:
            self._filteredNotes = self._notes


    def loadData(self,):
        self._notes = [Note(uid=file.decode('utf-8')) \
                       for file in os.listdir(Note.NOTESPATH) \
                       if (os.path.isfile(os.path.join(Note.NOTESPATH, file))) \
                       and (file != '.index.sync')]

        self._notes.sort(key=lambda note: note.timestamp, reverse=True)

    def rowCount(self, parent=QModelIndex()):
        return len(self._filteredNotes)

    def data(self, index, role):
        if index.isValid() and role == NotesModel.COLUMNS.index('title'):
            return self._filteredNotes[index.row()].title
        elif index.isValid() and role == NotesModel.COLUMNS.index('timestamp'):
            return self._filteredNotes[index.row()].human_timestamp
        elif index.isValid() and role == NotesModel.COLUMNS.index('uuid'):
            return self._filteredNotes[index.row()].uuid
        elif index.isValid() and role == NotesModel.COLUMNS.index('index'):
            return index.row()
        elif index.isValid() and role == NotesModel.COLUMNS.index('data'):
            return self._filteredNotes[index.row()].data
        return None

    @Slot()
    def reload(self):
        self.beginResetModel()
        self.loadData()
        self._filterNotes()
        self.endResetModel()


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
        self.notesModel = NotesModel()
        self.note = Note()
        self.conboyImporter = TomboyImporter()
        self.syncer = Sync()
        self.rootContext = self.view.rootContext()
        self.rootContext.setContextProperty("argv", sys.argv)
        self.rootContext.setContextProperty("__version__", __version__)
        self.rootContext.setContextProperty("__upgrade__", __upgrade__.replace('\n','<br>'))
        self.rootContext.setContextProperty("Settings", Settings())
        self.rootContext.setContextProperty("Sync", self.syncer)
        self.rootContext.setContextProperty("Importer", self.conboyImporter)
        self.rootContext.setContextProperty("QmlDirReaderWriter",
                                             QmlDirReaderWriter())
        self.rootContext.setContextProperty('notesModel', self.notesModel)
        self.rootContext.setContextProperty('Note', self.note)
        self.view.setSource(QUrl.fromLocalFile(
                os.path.join(os.path.dirname(__file__), 'qml', 'Harmattan_main.qml')))
        self.rootObject = self.view.rootObject()
        self.view.showFullScreen()
        self.note.on_error.connect(self.rootObject.onError)
        self.syncer.on_error.connect(self.rootObject.onError)
        self.syncer.on_finished.connect(self.notesModel.reload)
        self.conboyImporter.on_finished.connect(self.notesModel.reload)

if __name__ == '__main__':
    sys.exit(KhtNotes().exec_())
