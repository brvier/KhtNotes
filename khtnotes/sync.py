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

import sys
from webdav.WebdavClient import *
import os.path
import os
import urllib2
import urllib
import urlparse
import json
import threading
from PySide.QtCore import QObject, Slot, Signal, Property
from note import Note
from settings import Settings
import decimal
import time
import json

def basename(path):
  return os.path.basename(path)

class Sync(QObject):
  '''Sync class'''

  def __init__(self,):
    QObject.__init__(self)
    self._running = False

  @Slot()
  def launch(self):
    ''' Sync the notes in a thread'''
    if not self._get_running():
        self._set_running(True)
        self.thread = threading.Thread(target=self._sync)
        self.thread.start()

  def _sync(self):
    '''Sync the notes with a webdav server'''
    #Read Settings
    settings = Settings()
    webdavHost = settings.webdavHost
    self.webdavBasePath = settings.webdavBasePath
    webdavLogin = settings.webdavLogin
    webdavPasswd = settings.webdavPasswd

    #Create Connection
    isConnected = False
    webdavConnection = CollectionStorer(webdavHost+self.webdavBasePath,
                                        validateResourceNames=False)
    #Test KhtNotes folder and authenticate
    authFailures = 0
    while authFailures < 3:
      try:
        webdavConnection.validate()
        isConnected = True
        break # break out of the authorization failure counter
      except AuthorizationError, e:
        if e.authType == "Basic":
          webdavConnection.connection.addBasicAuthorization(webdavLogin, webdavPasswd)
        elif e.authType == "Digest":
          info = parseDigestAuthInfo(e.authInfo)
          webdavConnection.connection.addDigestAuthorization(webdavLogin, webdavPasswd, realm=info["realm"], qop=info["qop"], nonce=info["nonce"])
        elif authFailure >= 2:
          print 'Wrong login password'
        else:
          print type(e), e
          self.on_error.emit(unicode(e) +':'+unicode(e))

      except Exception, err:
        self.on_error.emit(unicode(type(err))+':'+unicode(err))
        print unicode(type(err))+':'+unicode(err)
      authFailures += 1

    if isConnected:
      self._check_khtnotes_folder_and_lock(webdavConnection)
      index_remote, deleted_remote = self._get_remote_index(webdavConnection)
      index_local, deleted_local = self._get_local_index()
      self._write_remote_index(webdavConnection)
      print 'Remote:', index_remote
      print 'Local:', index_local
      #Remotly deleted
      for filename in set(index_local).intersection(set(deleted_remote)):
        if index_local[filename]>deleted_remote[filename]:
          self._upload(webdavConnection, filename)
        else:
          self._local_delete(filename)
      #Locally deleted
      for filename in set(index_remote).intersection(set(deleted_local)):
        if index_remote[filename]>deleted_remote[filename]:
          self._download(webdavConnection, filename)
        else:
          self._remote_delete(webdavConnection, filename)
      #Updated
      for filename in set(index_remote).intersection(set(index_local)):
        if index_remote[filename]>index_local[filename]:
          self._download(webdavConnection, filename)
        elif index_remote[filename]<index_local[filename]:
          self._upload(webdavConnection, filename)        
        #Else we are already uptodate
      #New remote
      for filename in set(index_remote) - (set(index_local)):
        self._download(webdavConnection, filename)
      #New local
      for filename in set(index_local) - (set(index_remote)):
        self._upload(webdavConnection, filename)

      self._unlock(webdavConnection)
    self._set_running(False)


  def _upload(self, webdavConnection, filename):
    #TODO set modification time
    print 'DEBUG: Upload', filename
    webdavConnection.path = self._get_notes_path() + filename
    fh = open(os.path.join(Note.NOTESPATH, filename), 'rb')
    webdavConnection.uploadFile(fh) 
    fh.close()

  def _download(self, webdavConnection, filename):
    #TODO set modification time
    print 'DEBUG: Download', filename
    webdavConnection.path = self._get_notes_path() + filename
    webdavConnection.downloadFile(os.path.join(Note.NOTESPATH, filename)) 

  def _remote_delete(self, webdavConnection, filename):
    #TODO
    print 'DEBUG: remote_delete', filename

  def _local_delete(self, filename):
    #TODO
    print 'DEBUG: locale_delete', filename

  def _write_remote_index(self, webdavConnection):
    #TODO
    pass

  def _unlock(self,filename):
    #TODO
    pass

  def _get_notes_path(self):
    khtnotesPath = self.webdavBasePath
    if not khtnotesPath.endswith('/'):
       return khtnotesPath + '/KhtNotes/'
    else:
       return khtnotesPath + 'KhtNotes/'

  def _check_khtnotes_folder_and_lock(self, webdavConnection):
    '''Check that khtnotes folder exists on webdav'''
    khtnotesPath = self._get_notes_path()
    if not khtnotesPath in webdavConnection.listResources().keys():
      webdavConnection.addCollection(khtnotesPath)
    #TODO : Lock

  def _get_remote_index(self, webdavConnection):
    '''Check Remote Index'''
    webdavConnection.path = self._get_notes_path() + '.deleted.sync'
    try:
      index = json.loads(webdavConnection.downloadContent())
    except WebdavError, err:
      if err.reason == 'Not Found':
         index = {'current':{}, 'deleted':{}}
      else:
         raise
    webdavConnection.path = self._get_notes_path()
    new_index = dict([(basename(resource), time.mktime(properties.getLastModified())) \
            for (resource, properties) \
            in webdavConnection.listResources().items()])
    for filename, timestamp in index['current']:
      if filename not in new_index.key():
        index['deleted'][filename] = timestamp
    return (new_index, index['deleted'])

  def _get_local_index(self):
    index = dict([(filename, os.path.getmtime(os.path.join(Note.NOTESPATH, filename))) for filename in os.listdir(Note.NOTESPATH)
                    if os.path.isfile(os.path.join(Note.NOTESPATH, filename))])
    delnotes = dict([(filename, os.path.getmtime(os.path.join(Note.DELETEDNOTESPATH, filename))) for filename in os.listdir(Note.NOTESPATH)
                    if os.path.isfile(os.path.join(Note.DELETEDNOTESPATH, filename))])
    return (index, delnotes)

  def _get_local_data(self, timedelta=0):
    data = {}
    index = {}

    notes = [Note(uid=file) for file in os.listdir(Note.NOTESPATH)
                    if os.path.isfile(os.path.join(Note.NOTESPATH, file))]
    delnotes = [file for file in os.listdir(Note.DELETEDNOTESPATH)
                    if os.path.isfile(os.path.join(Note.DELETEDNOTESPATH, file))]


  def _write(self, uid, data, timestamp=None):
    ''' Write the document to a file '''
    note = Note(uid=uid)
    note.write(data)
    if timestamp != None:
        note.overwrite_timestamp()

  def _get_running(self):
    return self._running
  def _set_running(self, b):
    self._running = b
    self.on_running.emit()

  on_error = Signal(unicode)
  on_running = Signal()
  running = Property(bool, _get_running, _set_running, notify=on_running)

if __name__ == '__main__':
  s = Sync()
  s.launch() 