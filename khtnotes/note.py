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

from PySide.QtCore import Slot, QObject, Signal, Property

import os
import datetime
import markdown2
import string

FILENAME_CHARS = "-_. %s%s" % (string.ascii_letters, string.digits)

def getValidFilename(filename):
    return ''.join(car for car in filename if car in FILENAME_CHARS)

class Note(QObject):
    ''' A class representing a note '''

    NOTESPATH = os.path.join(os.path.expanduser('~'), '.khtnotes')

    def __init__(self, uid=None):
        QObject.__init__(self)
        self._title = u'Untitled'
        self._data = u''
        self._timestamp = None
        self._ready = False
        self._human_timestamp = u''
        print 'INIT:', uid
        if uid:
            self.load(uid)

    @Slot()
    def create(self):
        index = 0
        path = os.path.join(self.NOTESPATH, 'Untitled')
        while (os.path.exists('%s %s.txt' % (path,  unicode(index)))):
            index = index + 1
        self._set_title('Untitled %s' % unicode(index))
        self._set_text('Untitled %s' % unicode(index))
        self._set_ready(True)

    def valideFilename(self, filename):
        return ''.join(car for car in filename if car in FILENAME_CHARS)

    @Slot(unicode, result=bool)
    def write(self, data):
        ''' Write the document to a file '''
        print 'write:', self._uuid

        #Deleted content
        if data == '':
            #if exist only
            if self._uuid:
                print 'content deleted, try to delete note'
                self.rm(self._uuid)
            return True

        title = data.split('\n', 1)[0]
        print 'write:title:', title
        if title != self._title:
            #It s a rename of the note
            print 'Note is renammed'
            new_path = os.path.join(self.NOTESPATH,
                                    title + '.txt')
            if os.path.exists(new_path):
                self.on_error.emit(u'Note title already exists')
                return False
            if self._uuid:
                os.rename(os.path.join(self.NOTESPATH, self._uuid), \
                          new_path)
            self._uuid = getValidFilename(title.strip() + '.txt')

        if not self._uuid:
            self._uuid = getValidFilename(title.strip() + '.txt')

        path = os.path.join(self.NOTESPATH, self._uuid)
        try:
            with open(path, 'wb') as fh:
                data = data.split('\n',1)
                if len(data)>=2:
                    fh.write(data[1])
                else:
                    fh.write('')
                self._set_timestamp(os.stat(path).st_mtime)
                self._set_title(self._data.split('\n', 1)[0])
                #self.onDataChanged.emit()
                print path, ' written'
        except Exception, e:
            print e
            raise e
            self.on_error.emit(str(e))
            return False
        return True

    @Slot(unicode)
    def exists(self, uuid):
        if os.path.exists(os.path.join(self.NOTESPATH, uuid + '.txt')):
            return True
        else:
            return False

    @Slot(unicode)
    def rm(self, uuid=None):
        if uuid:
            self._uuid = uuid
        try:
            os.remove(os.path.join(self.NOTESPATH, self._uuid))
        except Exception, e:
            self.on_error.emit(str(e))

    def overwrite_timestamp(self, timestamp):
        try:
            os.utime(os.path.join(self.NOTESPATH, self._uuid),
                     (timestamp, timestamp))
        except OverflowError, overflow:
            import time
            os.utime(os.path.join(self.NOTESPATH, self._uuid),
                     (time.time(), time.time()))
            print overflow

    @Slot(unicode)
    def load(self, uid):
            #index = 0
            #path = os.path.join(self.NOTESPATH, 'Untitled ')
            #while (os.path.exists('%s %s.txt' % (path,  unicode(index)))):
            #  index =+ 1
            #self._set_uuid('Untitled %s.txt' % unicode(index))
            #self._set_title('Untitled %s' % unicode(index))
            #self._set_text('Untitled %s' % unicode(index))
            #self._set_ready(True)
        self._uuid = uid

        if (self._uuid):
            try:
                path = os.path.join(self.NOTESPATH, str(self._uuid))
                print 'path: ', path
                with open(path, 'rb') as fh:
                    try:
                        self._set_text(os.path.splitext(self._uuid)[0] + '\n' + unicode(fh.read(), 'utf-8'))
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
            return markdown2.markdown(text)
        except Exception, e:
            print type(e),':',e
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
        self._human_timestamp = \
            datetime.datetime.fromtimestamp(self._timestamp).strftime('%x %X')
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
    human_timestamp = Property(unicode, _get_human_timestamp,
                                 notify=onHumanTimestampChanged)
    data = Property(unicode, _get_text, _set_text, notify=onDataChanged)
    title = Property(unicode, _get_title, _set_title, notify=onTitleChanged)
    uuid = Property(unicode, _get_uuid, _set_uuid, notify=onUuidChanged)
    timestamp = Property(int, _get_timestamp, _set_timestamp,
                                 notify=onTimestampChanged)
    ready = Property(bool, _get_ready, _set_ready, notify=onReadyChanged)
