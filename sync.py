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

import urllib2
import json
import threading
from PySide.QtCore import QObject, Slot, Signal, Property

URL = 'http://khertan.net/khtnotes/sync.php'
LOGIN = 'demo'
PASSWORD = 'demo'

class Syncer(QObject):
  '''Sync class'''

  def __init__(self, url, login, password):
    QObject.__init__(self)
    self._url = url
    self._login = login
    self._password = password
    self._running = False

  @Slot(unicode)
  def launch(self):
    ''' Sync the notes in a thread'''
    self._set_running(True)
    self.thread = threading.Thread(target=self._sync)
    self.thread.start()

  def _sync(self):
    ''' Sync the notes'''
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, self._url, self._login, self._password)
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    jsoncontent = json.load(urllib2.urlopen(self._url))

    print jsoncontent    

    self._set_running(False)

  def _write(self, uid, data):
    ''' Write the document to a file '''
    try:
      with open(self.filepath, 'wb') as fh:
        fh.write(data.encode('utf-8'))
    except Exception, e:
      self.on_error.emit(str(e))

  def _get_running(self):
    return self._running
  def _set_running(self, b):
    self._running = b
    self.on_running.emit()
 
  on_error = Signal(unicode)
  on_running = Signal()
  running = Property(bool, _get_running, _set_running, notify=on_running) 

if __name__ == '__main__':
  s = Syncer('http://khertan.net/khtnotes/sync.php', 'demo', 'demo')
  s.launch() 