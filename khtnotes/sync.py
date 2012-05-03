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
import urlparse
import json
import threading
from PySide.QtCore import QObject, Slot, Signal, Property
from note import Note
from settings import Settings
import decimal
import time

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

  def _get_data(self, timedelta=0):
    
    data = {}
    index = {}    
    
    notes = [Note(uid=file) for file in os.listdir(Note.NOTESPATH) if os.path.isfile(os.path.join(Note.NOTESPATH, file))]        
    delnotes = [file for file in os.listdir(Note.DELETEDNOTESPATH) if os.path.isfile(os.path.join(Note.DELETEDNOTESPATH, file))]

    for note in notes:
        print 'DEBUG: UUID:', note.uuid, 'Timespamp:', self.toJsTimestamp(note.timestamp - timedelta)
        index[note.uuid] = {'timestamp': self.toJsTimestamp(note.timestamp - timedelta),
                            'title':note.title,}
        data[note.uuid] = json.dumps({"entry-id":note.uuid,"entry-content":note.data})

    for noteuuid in delnotes:
        index[noteuuid] = {'timestamp':0,
                            'title':'',}                            
        data[noteuuid] = json.dumps({"entry-id":noteuuid,"entry-content":''})
        
    data['index'] = json.dumps(index)
    data['clientime'] = self.toJsTimestamp(time.time())
    
    return (data, index, notes, delnotes)

  def toPyTimeStamp(self, jstimestamp):
    ''' Convert Javascript timestamp (since epoch in milliseconds) to Unix timestamp'''
    if type(jstimestamp) == unicode:
        return decimal.Decimal(jstimestamp) / 1000
    return decimal.Decimal(unicode(jstimestamp / 1000))
    
  def toJsTimestamp(self, pytimestamp):
    ''' Convert Unix timestamp (since epoch in seconds) to Javascript timestamp'''
    if type(pytimestamp) == unicode:
        return long(pytimestamp) * 1000
    return long(pytimestamp * 1000)
        
  def _sync(self):
    ''' Sync the notes'''
    
    try:
        settings = Settings()

        #Dummy request to calc time delta with server
        urlfordummyrequest = urlparse.urlparse(settings.syncUrl)
        response = urllib2.urlopen(urlfordummyrequest.scheme +'://'+urlfordummyrequest.netloc, urllib.urlencode({}))
        remote_time_str = response.info()['Date']
        try:
            time_delta = time.mktime(time.strptime(remote_time_str, '%a, %d %b %Y %H:%M:%S %Z')) - time.mktime(time.gmtime())
        except:
            try:
                time_delta = time.mktime(time.strptime(remote_time_str, '%a, %d %b %Y %H:%M:%S +0000')) - time.mktime(time.gmtime())
            except:
                print 'Can t get server time'
                time_delta = 0                
        print 'Time delta with server:', time_delta
        
        #Time delta require that all client use it, which isn't the case
        #yet for the web client        
        time_delta = 0        

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, settings.syncUrl, settings.syncLogin, settings.syncPassword)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)        
        opener = urllib2.build_opener(authhandler)    
        urllib2.install_opener(opener)
        local_data,local_index, local_notes , local_delnotes = self._get_data()
        print settings.syncUrl
        response = urllib2.urlopen(settings.syncUrl, urllib.urlencode(local_data))
        
        response = response.read()
        print response
        remote_data = json.loads(response)
        remote_index = remote_data['index']
        remote_entries = remote_data['entries']

        #As server sync reply only what should exit we delete what don't exist on server
        [Note(uid).rm() for uid in [note.uuid for note in local_notes] if uid not in remote_index]        

        if not remote_entries == []: #Server return 0 entries if nothing changes
            for rindex in remote_index:
                #remote_index = json.loads(rindex)
                ridata = remote_index[rindex]
                remote_timestamp = self.toPyTimeStamp(ridata['timestamp']) + decimal.Decimal(unicode(time_delta))
                #if remote_timestamp > 0 :
                #    remote_timestamp = remote_timestamp - decimal.Decimal(unicode(time_delta))
                if rindex in local_index:
                    #Server sync.php compute everythings, integrate directly
                    note = Note(uid=rindex)
                    print 'DEBUG: Remote timestamp:', time.localtime(float(remote_timestamp)), 'Local timestamp:', time.localtime(float(self.toPyTimeStamp(local_index[rindex]['timestamp']))), 'Title:', note.title
                    if rindex in remote_entries: #server think there is nothing new
                        note.write(remote_entries[rindex]['entry-content']) 
                    print remote_timestamp, ':', ridata['timestamp']
                    note.overwrite_timestamp(float(remote_timestamp ))

                    #local_timestamp = self.toPyTimeStamp(local_index[rindex]['timestamp'])
                    #print 'DEBUG: local, remote', local_timestamp , remote_timestamp, Note(rindex).title
                    #if remote_timestamp == 0 : #Remote entry has been deleted, remove the local too
                    #    Note(rindex).rm()
                    #elif os.path.exists(os.path.join(Note.DELETEDNOTESPATH,rindex)): #Local entry has been deleted, remove lo   
                    #    pass
                    #elif remote_timestamp > local_timestamp: # Remote entry is newer, get it                    
                    #    #print 'DEBUG remote entry newer : ' , remote_entries[rindex]
                    #    if rindex in remote_entries: #server think there is nothing new
                    #        note = Note(uid=rindex)
                    #        note.write(remote_entries[rindex]['entry-content'])
                    #        note.overwrite_timestamp(float(remote_timestamp))
                    #elif remote_timestamp < local_timestamp: # Local entry is newer, don't get it
                    #    pass
                    #else:
                    #    pass
                else:    # Else we store it
                    note = Note(uid=rindex)
                    note.write(remote_entries[rindex]['entry-content']) 
                    print remote_timestamp, ':', ridata['timestamp']
                    note.overwrite_timestamp(float(remote_timestamp ))
 

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
