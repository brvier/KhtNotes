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

import re
import os
import datetime
import codecs
from markdown import markdown
import htmlentitydefs
from settings import Settings

INVALID_FILENAME_CHARS = '\/:*?"<>|'

def getValidFilename(filename):
    return ''.join(car for car in filename \
                if car not in INVALID_FILENAME_CHARS)

def _strongify(group):
    return '<b>%s</b>' % group.group(0)

def _emify(group):
    return '<i>%s</i>' % group.group(0)

def _linkify(group):
     return '<font color="#00FF00">%s</font>' % group.group(0)

def _colorize(text):
    text = text.replace('\n', '<br>\n')
    regexs =  (
                (re.compile(
                    r'(\*|_){2}(.+?)(\*|_){2}',
                    re.UNICODE), _strongify),
                (re.compile(
            r'(?<!\*|_)(\*|_)(?!\*|_)(.+?)(?<!\*|_)(\*|_)(?!\*|_)',
                    re.UNICODE), _emify),
                (re.compile(
r'\[(.*?)\]\([ \t]*(&lt;(.*?)&gt;|(.*?))([ \t]+(".*?"))?[ \t]*\)',
                    re.UNICODE), _linkify),
              )
    for regex, cb in regexs:
        text = re.sub(regex, cb, text)

    return  u'%s' % text

def _unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError, e:
                print e
        else:
            # named entity
            try:
                text = unichr(
                    htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError, e:
                print e
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def _stripTags(content):
    ''' Remove html text formating from a text'''
    from BeautifulSoup import BeautifulSoup
    content = content.replace(
                '<p style=', '<pre style').replace(
                '<br />', '\n')
    plainText = _unescape(''.join(BeautifulSoup(
                content).body(text=True)))
    if (plainText.startswith('\n')):
        return plainText[1:]
    return plainText


def _uncolorize(text):
    return _stripTags(text)



class Note(QObject):
    ''' A class representing a note '''

    NOTESPATH = os.path.join(os.path.expanduser('~'), '.khtnotes')

    def __init__(self, uid=None):
        QObject.__init__(self, parent=None)
        self._title = None
        self._data = u''
        self._timestamp = None
        self._uuid = None
        self._ready = False
        self._human_timestamp = u''
        self._favorited = False
        self._settings = Settings()
        if uid:
            self.load(uid)

    @Slot()
    def create(self):
        index = 0
        path = os.path.join(self.NOTESPATH, 'Untitled')
        while (os.path.exists('%s %s.txt' % (path, unicode(index)))):
            index = index + 1
        self._set_text('Untitled %s' % unicode(index))
        self._title = None
        self._uuid = None
        self._favorited = False
        self._set_ready(True)

    @Slot(unicode, result=bool)
    def write(self, data):
        ''' Write the document to a file '''
        print data
        #Deleted content
        if data == '':
            #if exist only
            if self._uuid:
                self.rm(self._uuid)
            return True
        else:
            'Write data'
            data = _uncolorize(data)

        title = data.split('\n', 1)[0]
        if (title != self._title) and self._title:
            #It s a rename of the note
            new_path = os.path.join(self.NOTESPATH,
                                    title + '.txt')
            if os.path.exists(new_path):
                self.on_error.emit(u'Note title already exists')
                return False
            if self._uuid:
                os.rename(os.path.join(self.NOTESPATH,
                                       self._uuid),
                          new_path)
            self._uuid = getValidFilename(title.strip() + '.txt')

        if not self._uuid:
            self._uuid = getValidFilename(title.strip() + '.txt')

        path = os.path.join(self.NOTESPATH, self._uuid)
        try:
            with codecs.open(path, 'w', 'utf_8') as fh:
                data = data.split('\n', 1)
                if len(data) >= 2:
                    fh.write(data[1])
                else:
                    fh.write('')
                self._set_timestamp(os.stat(path).st_mtime)
                self._set_title(self._data.split('\n', 1)[0])
        except Exception, e:
            import traceback
            print traceback.format_exc()
            self.on_error.emit(str(e))
            return False
        return True

    @Slot(unicode)
    def exists(self, uuid):
        if os.path.exists(os.path.join(
            self.NOTESPATH, uuid + '.txt')):
            return True
        else:
            return False

    @Slot(unicode)
    def favorite(self, uuid=None):
        if uuid:
            if not self._settings.is_favorited(uuid):
                self._settings.add_favorite(uuid)
            else:
                self._settings.remove_favorite(uuid)

    @Slot(unicode)
    def duplicate(self,):
        import shutil
        src = os.path.join(self.NOTESPATH, self._uuid)
        new_uid = os.path.splitext(self._uuid)[0] + ' 2.txt'
        dst = os.path.join(self.NOTESPATH, new_uid)
        shutil.copy2(src, dst)
        return new_uid

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
        self._uuid = uid

        if (self._uuid):
            try:
                path = os.path.join(self.NOTESPATH, self._uuid)
                self._favorited = self._settings.is_favorited(uid)
                print self._favorited
                self.onFavoritedChanged.emit()

                with codecs.open(path, 'r', 'utf_8') as fh:
                    try:
                        text = fh.read()
                        if text.find('\0') > 0:
                            #Probably utf-16 ... decode it to utf-8
                            #as qml didn t support it well'
                            text = text.decode('utf-16')
                        title = os.path.splitext(self._uuid)[0]
                        self._set_text(title \
                                    + '\n' + text)
                        self._set_timestamp(os.stat(path).st_mtime)
                        self._set_title(title)
                        self._set_ready(True)
                    except Exception, e:
                        print e
                        import traceback
                        print traceback.format_exc()
                        self.on_error.emit(str(e))
                        self._set_ready(True)
            except Exception, e:
                import traceback
                print traceback.format_exc()
                print e
                self.on_error.emit(str(e))

    @Slot(unicode, result=unicode)
    def previewMarkdown(self, text):
        ''' Generate a markdown preview'''
        try:
            return markdown(_uncolorize(text), extensions=['nb2lr',])
        except Exception, e:
            print type(e), ':', e
            return text

    def _get_text(self):
        return self._data

    def _set_text(self, text):
        self._data = _colorize(text)
        self.onDataChanged.emit()

    def _get_favorited(self):
        return self._favorited

    def _set_favorited(self, value):
        self._favorited = value
        if value:
            self._settings.add_favorite(self._uuid)
        else:
            self._settings.remove_favorite(self._uuid)
        self.onFavoritedChanged.emit()

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
            datetime.datetime.fromtimestamp(
                self._timestamp).strftime('%x %X')
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
    onFavoritedChanged = Signal()
    human_timestamp = Property(unicode, _get_human_timestamp,
                                 notify=onHumanTimestampChanged)
    data = Property(unicode,
                    _get_text,
                    _set_text,
                    notify=onDataChanged)
    title = Property(unicode,
                     _get_title,
                     _set_title,
                     notify=onTitleChanged)
    uuid = Property(unicode,
                    _get_uuid,
                    _set_uuid,
                    notify=onUuidChanged)
    timestamp = Property(int,
                    _get_timestamp, _set_timestamp,
                    notify=onTimestampChanged)
    favorited = Property(bool,
                         _get_favorited,
                         _set_favorited,
                         notify=onFavoritedChanged)
    ready = Property(bool,
                     _get_ready,
                     _set_ready,
                     notify=onReadyChanged)

if __name__ == '__main__':
    print _colorize('Test\ntest **test**, test haha __test__, hahaha test__test__test and an other *test* [link](http://khertan.net/)')
