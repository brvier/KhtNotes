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
from PySide.QtCore import QUrl, Slot, Property, \
    QAbstractListModel, QModelIndex, QEvent
from PySide import QtDeclarative
from PySide.QtOpenGL import QGLWidget, QGLFormat

import sys
import os
import os.path

from settings import Settings
from note import Note
from sync import Sync
from importer import TomboyImporter

__author__ = 'Benoit HERVIER (Khertan)'
__email__ = 'khertan@khertan.net'
__version__ = '3.7'
__build__ = '1'
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
1.10: Fix creation of KhtNotes folder on webdav and
      avoid lose of notes in case of notes if path is created,
      improve sync and fix bugs on conflicting update
2.0: Formatted notes when markdown syntax is used
2.1: Fix the formatting of notes
2.2: Fix a bug in sync when a file conflict happen
2.3: Avoid useless conflict
2.4: Magically merge conflicting notes
2.5: Add setting for using auto merging feature or not
2.6: Fix directory error in copying files for merge
2.7: Fix an other directory error in copying files for merge
2.8: Remove absolute import for merge3: which fix import error error
2.9: Fix the sync without and with merge feature
2.10: Add favorite feature, add duplicate, improve delete,
      fix markdown preview, add realtime markdown highlight
2.11: Darker color and bigger text for title highlight,
      improve pre/post package script, fix timer for realtime highlight
2.12: Fix markdown preview (new line extension)
2.13: Use more limited set of html due to limitation on Qt.TextEdit
2.14: Unactivate opengl for Mer/Nemo OS
2.15: Fix a bug losing focus when refreshing highlighting and add
      privacy policy in about screen
2.16: Fix an error in the settings parser that prevent it using the right
      password to authenticate to a webdav account
      Fix an error preventing displaying a login / password error message
2.17: Add 64x64 icon for nemo mobile, clean make.py
2.18: Fix an mistake where timedelta didn't care of timezone of server
2.19: Add a preferences for the remote folder name (Default is now Notes)
2.20: Better preferences setting page add text size setting, better detection
      if we use opengl or not (only used for harmattan), code cleaning
2.21: Remove \r line ending
      Wrap Everywhere instead of wordwrap
      Avoid flagging just opened note as modified
      Fix a bug where synced file time was set in UTC instead of localtime
3.0 : Implement category and fix some nasty sync bugs, add automatic sync
3.1 : Improve sync again
3.2 : Fix autoSync that didn t take care of preference setting
      Fix an autoSync bug that block the ui due to refresh while editing
      Fix an bug on notes when title lenght exceed what filesystem support
3.3 : Fix wordWrap in about page
3.4 : Improve hide vkb keyboard
      Improve settings
3.5 : Fix a bug where notes with just a title aren't saved
3.6 : Add harmattan share ui export feature
      Add http://scriptogr.am post feature
3.7 : Add missing dependency python-dbus
      Test size file on conflict merge to avoid a bug in ownCloud webdav'''


class NotesModel(QAbstractListModel):
    COLUMNS = ('title', 'timestamp', 'uuid', 'index',
               'data', 'favorited', 'category')

    def __init__(self, ):
        self._notes = []
        QAbstractListModel.__init__(self)
        self.setRoleNames(dict(enumerate(NotesModel.COLUMNS)))
        self._filter = None
        self._filteredNotes = self._notes
        self._categories = []

        if not os.path.exists(Note.NOTESPATH):
            try:
                os.mkdir(Note.NOTESPATH)
            except Exception, e:
                print 'Can t create note storage folder', str(e)

        # self.loadData()

    @Slot(unicode)
    def setFilterFixedString(self, search):
        self._filter = search
        self.beginResetModel()
        self._filterNotes()
        self.endResetModel()

    def _filterNotes(self):
        if self._filter:
            self._filteredNotes = [note for note in self._notes
                                   if self._filter.lower()
                                   in note.title.lower()]
        else:
            self._filteredNotes = self._notes

    def loadData(self,):
        self._notes = []
        self._categories = []
        for root, folders, filenames in os.walk(Note.NOTESPATH):
                category = os.path.relpath(root, Note.NOTESPATH)
                if category == u'.':
                    category = u''
                if category != '.merge.sync':
                    self._notes.extend(
                        [Note(uid=os.path.join(category, unicode(filename)))
                         for filename in filenames
                         if filename != '.index.sync'])
                    self._categories.append(category)

        self._sortData()

    def _sortData(self,):
        self._notes.sort(key=lambda note: (not note.favorited,
                                           note.category,
                                           note.title),
                         reverse=False)
        self._categories.sort()

    def rowCount(self, parent=QModelIndex()):
        return len(self._filteredNotes)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == 0:  # NotesModel.COLUMNS.index('title'):
            return self._filteredNotes[index.row()].title
        elif role == 1:  # NotesModel.COLUMNS.index('timestamp'):
            return self._filteredNotes[index.row()].human_timestamp
        elif role == 2:  # NotesModel.COLUMNS.index('uuid'):
            return self._filteredNotes[index.row()].uuid
        elif role == 3:  # NotesModel.COLUMNS.index('index'):
            return index.row()
        elif role == 4:  # NotesModel.COLUMNS.index('data'):
            return self._filteredNotes[index.row()].data
        elif role == 5:  # NotesModel.COLUMNS.index('favorited'):
            return self._filteredNotes[index.row()].favorited
        elif role == 6:  # NotesModel.COLUMNS.index('category'):
            return self._filteredNotes[index.row()].category

        return None

    @Slot()
    def get(self, index):
        return self._filteredNotes[index.row()]

    @Slot()
    def reload(self):
        self.beginResetModel()
        self.loadData()
        self._filterNotes()
        self.endResetModel()

    @Slot(int)
    def favorite(self, idx):
        self.beginResetModel()
        self._filteredNotes[idx].favorited = not \
            self._filteredNotes[idx].favorited
        self._sortData()
        self.endResetModel()

    @Slot(int)
    def duplicate(self, idx):
        self.beginResetModel()
        uuid = self._filteredNotes[idx].duplicate()
        self._notes.append(Note(uuid))
        self._filterNotes()
        self._sortData()
        self.endResetModel()

    @Slot(int)
    def remove(self, idx):
        self.beginResetModel()
        uuid = self._filteredNotes[idx].uuid
        self._filteredNotes[idx].rm()
        for note in self._notes:
            if note.uuid == uuid:
                self._notes.remove(note)
                break
        self._filterNotes()
        self._sortData()
        self.endResetModel()

    @Slot(result=unicode)
    def getCategories(self,):
        return '\n'.join(self._categories)

    @Slot(int, unicode)
    def setCategory(self, idx, name):
        self.beginResetModel()
        self._filteredNotes[idx].category = name
        self.loadData()
        self._filterNotes()
        self._sortData()
        self.endResetModel()

    count = Property(int, rowCount)


class FilteredDeclarativeView(QtDeclarative.QDeclarativeView):
    def __init__(self, settings=None):
        QtDeclarative.QDeclarativeView.__init__(self)
        if settings:
            self.settings = settings
        else:
            self.settings = Settings()

    def event(self, event):
        if ((event.type() == QEvent.RequestSoftwareInputPanel)
                and (self.settings.hideVkb)):
            # Hacky way to do, but event is already processed when
            # python got the hand
            closeEvent = QEvent(QEvent.CloseSoftwareInputPanel)
            QApplication.instance().postEvent(self, closeEvent)
            return True
        return QtDeclarative.QDeclarativeView.event(self, event)


class KhtNotes(QApplication):
    ''' Application class '''
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        self.setOrganizationName("Khertan Software")
        self.setOrganizationDomain("khertan.net")
        self.setApplicationName("KhtNotes")

        self.settings = Settings()
        self.view = FilteredDeclarativeView(settings=self.settings)
        if os.path.exists('/etc/mer-release'):
            fullscreen = True
        elif os.path.exists('/etc/aegis'):
            fullscreen = True
            self.glformat = QGLFormat().defaultFormat()
            self.glformat.setSampleBuffers(False)
            self.glw = QGLWidget(self.glformat)
            self.glw.setAutoFillBackground(False)
            self.view.setViewport(self.glw)
        else:
            fullscreen = False

        self.notesModel = NotesModel()
        self.note = Note(settings=self.settings)
        self.conboyImporter = TomboyImporter()
        self.syncer = Sync()
        self.rootContext = self.view.rootContext()
        self.rootContext.setContextProperty("argv", sys.argv)
        self.rootContext.setContextProperty("__version__", __version__)
        self.rootContext.setContextProperty("__upgrade__", __upgrade__
                                            .replace('\n', '<br />'))
        self.rootContext.setContextProperty("Settings", self.settings)
        self.rootContext.setContextProperty("Sync", self.syncer)
        self.rootContext.setContextProperty("Importer", self.conboyImporter)
        self.rootContext.setContextProperty('notesModel', self.notesModel)
        self.rootContext.setContextProperty('Note', self.note)

        try:
            self.view.setSource(QUrl.fromLocalFile(
                os.path.join(os.path.dirname(__file__),
                             'qml', 'Harmattan_main.qml')))
        except:
            self.view.setSource(QUrl.fromLocalFile(
                os.path.join(os.path.dirname(__file__),
                             'qml', 'Desktop_main.qml')))

        self.rootObject = self.view.rootObject()
        if fullscreen:
            self.view.showFullScreen()
        else:
            self.view.show()
        self.note.on_error.connect(self.rootObject.onError)
        self.syncer.on_error.connect(self.rootObject.onError)
        self.syncer.on_finished.connect(self.rootObject.refresh)
        self.conboyImporter.on_finished.connect(self.notesModel.reload)

if __name__ == '__main__':
    sys.exit(KhtNotes().exec_())   