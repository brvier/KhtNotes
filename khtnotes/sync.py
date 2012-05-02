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

import os
import urllib2
import urllib
import json
import threading
from PySide.QtCore import QObject, Slot, Signal, Property
from note import Note
from settings import Settings
import decimal

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

  def _get_data(self):
    
    data = {}
    index = {}    
    
    notes = [Note(uid=file) for file in os.listdir(Note.NOTESPATH) if os.path.isfile(os.path.join(Note.NOTESPATH, file))]        
    delnotes = [file for file in os.listdir(Note.DELETEDNOTESPATH) if os.path.isfile(os.path.join(Note.DELETEDNOTESPATH, file))]

    for note in notes:
        print 'note.timestamp:',note.timestamp
        index[note.uuid] = {'timestamp':note.timestamp,
                            'title':note.title,}
        data[note.uuid] = json.dumps({"entry-id":note.uuid,"entry-content":note.data})

    for noteuuid in delnotes:
        index[noteuuid] = {'timestamp':0,
                            'title':'',}                            
        data[noteuuid] = json.dumps({"entry-id":noteuuid,"entry-content":''})
        
    data['index'] = json.dumps(index)
    return (data, index, notes, delnotes)

  def _timestamp_fix(self,timestamp):
    ''' Fix the timestamp to be conform to py timestamp '''
    if type(timestamp) == unicode:
        if len(timestamp) <= 14:
           timestamp = '%s.%s' % (timestamp[:9], timestamp[10:])
    if type(timestamp) == float:
        timestamp = unicode(timestamp)
    return decimal.Decimal(timestamp)
        #timestamp = decimal(timestamp)
    
  def _sync(self):
    ''' Sync the notes'''
    
    try:
        settings = Settings()

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, settings.syncUrl, settings.syncLogin, settings.syncPassword)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)    
        urllib2.install_opener(opener)

        local_data,local_index, local_notes , local_delnotes = self._get_data()
        response = urllib2.urlopen(settings.syncUrl, urllib.urlencode(local_data))

        response = response.read()
        print 'Response:', response
        remote_data = json.loads(response)
        remote_index = remote_data['index']
        remote_entries = remote_data['entries']
        
        #As server sync reply only what should exit we delete what don't exist on server
        [Note(uid).rm() for uid in [note.uuid for note in local_notes] if uid not in remote_index]        

        for rindex in remote_index:
            #remote_index = json.loads(rindex)
            ridata = remote_index[rindex]
            remote_timestamp = self._timestamp_fix(ridata['timestamp'])
            local_timestamp = self._timestamp_fix(local_index[rindex]['timestamp'])
            if rindex in local_index:
                if remote_timestamp == 0 : #Remote entry has been deleted, remove the local too
                    Note(rindex).rm()
                    print 'DEBUG: delete:', rindex
                elif os.path.exists(os.path.join(Note.DELETEDNOTESPATH,rindex)): #Local entry has been deleted, remove lo   
                    print 'Exists in deleted folder'
                elif remote_timestamp > local_timestamp: # Remote entry is newer, get it                    
                    print 'DEBUG remote entry newer : ' , remote_entries[rindex]
                    print 'timestamp:', remote_timestamp, '(', type(remote_timestamp), '),', local_timestamp, ':(', type(local_timestamp), ')'
                    note = Note(uid=rindex)
                    note.write(remote_entries[rindex]['entry-content'])
                    note.overwrite_timestamp(remote_timestamp)
                elif remote_timestamp < local_timestamp: # Local entry is newer, don't get it
                    print 'DEBUG: Local entry newer:', remote_timestamp, '(', type(remote_timestamp), '),', local_timestamp, ':(', type(local_timestamp), ')'
                else:
                    print 'DEBUG: Local entry same timestamp'
            else:    # Else we store it
                note = Note(uid=rindex)
                note.write(remote_entries[rindex]['entry-content']) 
                note.overwrite_timestamp(remote_timestamp)
 

    except Exception, e:
        import traceback
        traceback.print_exc()
        print type(e), ':', e
        self.on_error.emit(str(e))
    
    self._set_running(False)
                  
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
