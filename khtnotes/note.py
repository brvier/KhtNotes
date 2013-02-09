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
from settings import Settings, NOTESPATH

INVALID_FILENAME_CHARS = '\/:*?"<>|'
STRIPTAGS = re.compile(r'<[^>]+>')
STRIPHEAD = re.compile("<head>.*?</head>", re.DOTALL)


def getValidFilename(filepath):
    dirname, filename = os.path.dirname(filepath), os.path.basename(filepath)
    return os.path.join(dirname, ''.join(car for car in filename
                        if car not in INVALID_FILENAME_CHARS))


def _strongify(group):
    return '<b>%s</b>' % group.group(0)


def _emify(group):
    return '<i>%s</i>' % group.group(0)


def _linkify(group):
    return '<font color="#00FF00">%s</font>' % group.group(0)


def _titleify(group):
    return '<big><font color="#441144">%s</font></big>' % group.group(0)


def _undertitleify(group):
    return '<big><font color="#663366">%s</font></big>' % group.group(0)


def _colorize(text):
    regexs = ((re.compile(
        r'(\*|_){2}(.+?)(\*|_){2}',
        re.UNICODE), _strongify),
        (re.compile(
            r'(?<!\*|_)(\*|_)(?!\*|_)'
            '(.+?)(?<!\*|_)(\*|_)(?!\*|_)',
            re.UNICODE), _emify),
        (re.compile(
            r'\[(.*?)\]\([ \t]*(&lt;(.*?)&gt;|(.*?))'
            '([ \t]+(".*?"))?[ \t]*\)',
            re.UNICODE), _linkify),
        (re.compile(
            '^(.+)\n=+$',
            re.UNICODE | re.MULTILINE), _titleify),
        (re.compile(
            r'^(.+)\n-+$',
            re.UNICODE | re.MULTILINE), _undertitleify),
        (re.compile(
            r'^#(.+)#$',
            re.UNICODE | re.MULTILINE), _titleify),
        (re.compile(
            r'^##(.+)##$',
            re.UNICODE | re.MULTILINE), _undertitleify),
    )
    for regex, cb in regexs:
        text = re.sub(regex, cb, text)
    #text = text.replace('\n', '</p><p>').replace('<p></p>', '<br />')
    text = text.replace('\r\n', '\n')
    text = text.replace('\n', '<br />')
    text = text.replace('\r', '')
    return  u'''
<html><head><style type="text/css">
    p, li, pre, body {
        white-space: pre-wrap;
        font-family: "Nokia Pure Text";
        margin-top: 0px;
        margin-bottom: 0px;}
</style><body><p>%s</p></body></html>''' % text


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
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)


def _uncolorize(text):
    text = _unescape(STRIPTAGS.sub('',
                     STRIPHEAD.sub('', text.replace('', '')
                                   .replace('\n<pre style="'
                                   + '-qt-paragraph-type:empty;'
                                   + ' margin-top:0px;'
                                   + ' margin-bottom:0px; margin-left:0px;'
                                   + ' margin-right:0px; -qt-block-indent:0;'
                                   + ' text-indent:0px;"><br /></pre>', '\n')
                                   .replace('\n<p style="'
                                   + '-qt-paragraph-type:empty;'
                                   + ' margin-top:0px; margin-bottom:0px;'
                                   + ' margin-left:0px; margin-right:0px;'
                                   + ' -qt-block-indent:0; text-indent:0px;'
                                   + '"><br /></p>', '\n')
                                   .replace('<br />', '\n'))))
    return text.lstrip('\n')


class Note(QObject):
    ''' A class representing a note '''

    NOTESPATH = NOTESPATH

    def __init__(self, uid=None, settings=None):
        QObject.__init__(self, parent=None)
        self._title = None
        self._data = u''
        self._timestamp = None
        self._uuid = None
        self._category = ''
        self._ready = False
        self._human_timestamp = u''
        self._favorited = False
        if settings:
            self._settings = settings
        else:
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
        self._category = ''
        self._favorited = False
        self._set_ready(True)

    @Slot(unicode, result=bool)
    def write(self, data):
        ''' Write the document to a file '''

        #Deleted content
        if data == '':
            #if exist only
            if self._uuid:
                self.rm(os.path.join(self._uuid))
            return True
        else:
            'Write data'
            data = _uncolorize(data)

        try:
            _title, _content = data.split('\n', 1)
        except ValueError, err:
            _title = data.split('\n', 1)[0]
            _content = ''

        if len(_title) > 255:
            title = _title[:255]
            _content = _title[256:] + _content
        else:
            title = _title
        if (title != self._title) and self._title:
            #It s a rename of the note
            new_path = os.path.join(self.NOTESPATH,
                                    self._category,
                                    title + '.txt')
            if os.path.exists(new_path):
                print 'Note title already exists: %s' % new_path
                self.on_error.emit(u'Note title already exists')
                return False
            if self._uuid:
                os.rename(os.path.join(self.NOTESPATH,
                                       #self._category,
                                       self._uuid),
                          new_path)
            self._uuid = os.path.join(self._category,
                                      getValidFilename(title.strip()
                                                       + '.txt'))

        if not self._uuid:
            self._uuid = os.path.join(self._category,
                                      getValidFilename(title.strip()
                                                       + '.txt'))

        path = os.path.join(self.NOTESPATH, self._uuid)
        try:
            with codecs.open(path, 'wb', 'utf_8') as fh:
                fh.write(_content)
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
    def favorite(self, uuid):
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
                self._category = os.path.dirname(self._uuid)
                self.onCategoryChanged.emit()
                self._favorited = self._settings.is_favorited(uid)
                self.onFavoritedChanged.emit()
                with codecs.open(path, 'rb',
                                 encoding='utf_8', errors='replace') as fh:
                    try:
                        text = fh.read()
                        if text.find('\0') > 0:
                            #Probably utf-16 ... decode it to utf-8
                            #as qml didn t support it well'
                            text = text.decode('utf-16')
                        title = os.path.splitext(
                            os.path.basename(self._uuid))[0]
                        self._set_text(title
                                       + '\n' + text)
                        self._set_timestamp(os.stat(path).st_mtime)
                        self._set_title(title)
                        self._set_ready(True)
                    except Exception, e:
                        print e
                        print 'path:', path
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
    def reHighlight(self, text):
        return _colorize(_uncolorize(text))

    @Slot(unicode, result=unicode)
    def previewMarkdown(self, text):
        ''' Generate a markdown preview'''
        try:
            return markdown(_uncolorize(text), extensions=['nl2br', ])
        except Exception, e:
            print type(e), ':', e
            return text

    @Slot(unicode, result=unicode)
    def previewReStructuredText(self, text):
        ''' Generate a markdown preview'''
        try:
            from docutils.core import publish_parts
            return publish_parts(_uncolorize(text), writer_name='html')['html_body']
        except Exception, e:
            print type(e), ':', e
            return text
   
    def _get_text(self):
        return self._data

    def _set_text(self, text):
        self._data = _colorize(text.replace('\r\n', '\n'))
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

    def _set_category(self, category):
        new_uuid = os.path.join(category, os.path.basename(self._uuid))
        if self.exists(new_uuid):
            self.on_error.emit('There is already a note with the same title')
            return
        try:
            old_uuid = self._uuid
            self._category = category
            self._set_uuid(new_uuid)
            if not os.path.exists(os.path.join(self.NOTESPATH,
                                               self._category)):
                os.mkdir(os.path.join(self.NOTESPATH, self._category))
            os.rename(os.path.join(self.NOTESPATH, old_uuid),
                      os.path.join(self.NOTESPATH, new_uuid))
            self.onCategoryChanged.emit()
        except Exception, e:
            self.on_error.emit(str(e))

    def _get_category(self):
        return self._category

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
    onCategoryChanged = Signal()
    category = Property(unicode,
                        _get_category,
                        _set_category,
                        notify=onCategoryChanged)
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
    print _colorize('Test\n====\ntest **test**, test haha __test__,'
                    ' hahaha test__test__test and an other *test* '
                    '[link](http://khertan.net/)'
                    '\ntest under title\n-------\ntest'
                    '\n## test ##\n# test #\ntest')     