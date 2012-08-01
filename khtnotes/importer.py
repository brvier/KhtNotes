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

import os.path
import glob
from xml.sax.handler import ContentHandler
import xml.sax
from note import Note, getValidFilename
import threading
from PySide.QtCore import QObject, Signal, Slot, \
                          Property


class TomboyImporter(QObject):
    def __init__(self,):
        QObject.__init__(self, None)
        self._running = False

    @Slot()
    def launch(self):
        ''' Sync the notes in a thread'''
        if not self._get_running():
            self._set_running(True)
            self.thread = threading.Thread(target=self._import)
            self.thread.start()

    def _import(self):
        self.noteList = {}
        for infile in glob.glob( \
            os.path.join(os.path.expanduser('~/.conboy'), '*.note')):
            try:
                parser = xml.sax.make_parser()
                handler = textHandler()
                parser.setContentHandler(handler)
                parser.parse(infile)
            except Exception, err:
                import traceback
                print traceback.format_exc()

            try:
                note = Note()
                uuid = handler._content.split('\n', 1)[0].strip(' \t\r\n')
                uuid = getValidFilename(uuid)
                path = os.path.join(note.NOTESPATH, uuid)
                if os.path.exists(path + '.txt'):
                    index = 2
                    while (os.path.exists(os.path.join( \
                            note.NOTESPATH,'%s %s.txt' \
                            % (path, \
                            unicode(index))))):
                        index = index + 1
                    uuid = ('%s %s' \
                            % (os.path.basename(path), \
                            unicode(index)))

                note.uuid = uuid + '.txt'
                note.write(handler._content)
                try:
                    from rfc3339.rfc3339 import strtotimestamp
                    mtime = strtotimestamp(handler._last_change)
                    lpath = os.path.join(Note.NOTESPATH, note.uuid)
                    os.utime(lpath, (-1, mtime))
                except Exception, err:
                    import traceback
                    print traceback.format_exc()

            except Exception, err:
                import traceback
                print traceback.format_exc()

        self._set_running(False)
        self.on_finished.emit()

    def _get_running(self):
        return self._running

    def _set_running(self, b):
        self._running = b
        self.on_running.emit()

    on_finished = Signal()
    on_error = Signal(unicode)
    on_running = Signal()
    running = Property(bool, _get_running, _set_running, notify=on_running)

class textHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self._content = u''
        self._title = u''
        self._last_change = u''
        self._selector = None
        self._list_level = 0

    def startElement(self, element,attributes):
        if (element == 'note-content') and (self._selector == None):
            self._selector = element
        elif (element == 'last-change-date') and (self._selector == None):
            self._selector = element
        elif (element == 'title') and (self._selector == None):
            self._selector = element
        elif (element == 'list'):
            self._list_level = self._list_level + 1
        elif (element == 'list-item'):
            self._content = self._content + '  ' * self._list_level + '*'
        elif (element == 'bold'):
            self._content = self._content + '**'
        elif (element == 'italic'):
            self._content = self._content + '*'
        elif (element == 'size:huge'):
            self._content = self._content + '#'
        elif (element == 'size:large'):
            self._content = self._content + '##'
        #else:
        #   print 'Element:', element

    def endElement(self, element):
        if (element == self._selector):
            self._selector = None
        elif (element == 'list'):
            self._list_level = self._list_level - 1
        elif (element == 'bold'):
            self._content = self._content + '**'
        elif element == 'italic':
            self._content = self._content + '*'
        #else:
        #    print 'End Element:', element

    def characters(self, ch):
        try:
            if self._selector == 'note-content':
                self._content = self._content + unicode(ch)
            elif self._selector == 'title':
                self._title = self._title + unicode(ch)
            elif self._selector == 'last-change-date':
                self._last_change = self._last_change + unicode(ch)
        except Exception, err:
             import traceback
             print traceback.format_exc()


if __name__ == '__main__':
    importer = TomboyImporter()
    importer.launch()
    while importer._running:
        pass
