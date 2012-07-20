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
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
## GNU General Public License for more details.

from webdav.WebdavClient import *
import os.path
import os
import threading
from PySide.QtCore import QObject, Slot, Signal, Property
from note import Note
from settings import Settings
import time


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
        self.webdavHost = settings.webdavHost
        self.webdavBasePath = settings.webdavBasePath
        webdavLogin = settings.webdavLogin
        webdavPasswd = settings.webdavPasswd

        #Create Connection
        isConnected = False
        webdavConnection = CollectionStorer(self.webdavHost + self.webdavBasePath,
                           validateResourceNames=False)
        #Test KhtNotes folder and authenticate
        authFailures = 0
        while authFailures < 3:
            try:
                webdavConnection.validate()
                isConnected = True
                break  # break out of the authorization failure counter
            except AuthorizationError, e:
                if e.authType == "Basic":
                    webdavConnection.connection.\
                        addBasicAuthorization(webdavLogin, webdavPasswd)
                elif e.authType == "Digest":
                    info = parseDigestAuthInfo(e.authInfo)
                    webdavConnection.connection.\
                        addDigestAuthorization(webdavLogin,
                                               webdavPasswd,
                                               realm=info["realm"],
                                               qop=info["qop"],
                                               nonce=info["nonce"])
                elif authFailure >= 2:
                    print 'Wrong login password'
                else:
                    print type(e), e
                    self.on_error.emit(unicode(e) + ':' + unicode(e))

            except Exception, err:
                self.on_error.emit(unicode(type(err)) + ':' + unicode(err))
                print unicode(type(err)) + ':' + unicode(err)
            authFailures += 1

        print 'DEBUG 3'
        if isConnected:
            print 'DEBUG 2'
            #Check that KhtNotes folder exists at root or create it and
            #and lock Collections
            self._check_khtnotes_folder_and_lock(webdavConnection)

            #Get remote filenames and timestamps
            remote_filenames = self._get_remote_filenames(webdavConnection)
            print 'DEBUG 4'
            #Get local filenames and timestamps
            local_filenames = self._get_local_filenames()

            #Compare with last sync index
            lastsync_remote_filename, \
            lastsync_local_filename = self._get_lastsync_filenames()

            #Sync intelligency (or not)
            #It use a local index with timestamp of the server files
            #1/ As most webdav server didn t support setting 
            #   modification datetime on ressources
            #2/ Main target is owncloud where webdavserver didn't
            #   implent delta-v versionning
            #3/ Notes should be editable in the owncloud interface
            #   but i would like to support other webdav server
            #   so an owncloud apps isn t acceptable


            #TODO: manage deleted
            ###Get updated remote
            ###fremote_deleted = set(lastsync_filename) - set(remote_filenames)

            print "DEBUG 1"

            #What to do with new remote file
            for filename in set(remote_filenames) \
                            - set(lastsync_remote_filename):
                if not filename in local_filenames.keys():
                    self._download(webdavConnection, filename)
                else:
                    #Conflict : it s a new file so we haven't sync it yet
                    #Todo: we should download it with an other name
                    self._conflictServer(webdavConnection, filename)

            #What to do with new local file
            for filename in set(local_filenames) \
                            - set(lastsync_local_filename):
                if not filename in remote_filenames.keys():
                    self._upload(webdavConnection, filename)
                else:
                    #Conflict : it s a new file so we haven't sync it yet
                    #Todo: we should upload it with an other name
                    self._conflictLocal(webdavConnection, filename)

            #Check what's updated remotly
            rupdated = [filename for filename \
                               in (set(remote_filenames).\
                               intersections(lastsync_remote_filename)) \
                               if remote_filenames[filename] \
                                  != lastsync_remote_filename[filename]]
            lupdated = [filename for filename \
                               in (set(local_filenames).\
                               intersections(lastsync_local_filename)) \
                               if remote_filenames[filename] \
                                  != lastsync_local_filename[filename]]
            for filename in set(rupdated) - set(lupdated):
                self._download(webdavConnection, filename)
            for filename in set(lupdated) - set(rupdated):
                self._upload(webdavConnection, filename)
            for filename in set(lupdated).intersection(rupdated):
                if remote_filenames[filename] > local_filenames[filename]:
                    self.conflictLocal(webdavConnection, filename)
                else:
                    self.conflictServer(webdavConnection, filename)

            #Build and write index
            self._write_index(webdavConnection)

            #Unlock the collection
            self._unlock(webdavConnection)

        self._set_running(False)

    def _conflictServer(self, webdavConnection, filename):
        '''Priority to local'''
        self._move(webdavConnection, filename, filename + '.Conflict')
        self._download(webdavConnection, filename + '.Conflict')
        self._upload(webdavConnection, filename)

    def _conflictLocal(self, webdavConnection, filename):
        '''Priority to server'''
        os.rename(os.path.join(Note.NOTESPATH, filename),
            os.path.join(Note.NOTESPATH, filename + '.Conflict'))
        self._upload(webdavConnection, filename + '.Conflict')
        self._download(webdavConnection, filename)

    def _get_lastsync_filenames(self):
        index = ({}, {})
        try:
            with open(os.path.join(Note.NOTESPATH, '.index.sync'), 'rb') as fh:
                index = json.load(fh)
        except IOError, err:
            print 'First sync detected or error:', err
        return index

    def _write_index(self, webdavConnection, filename):
        '''Generate index for the last sync'''
        index = (self._get_remote_filenames(webdavConnection),
                 self._get_local_filenames())
        with open(os.path.join(Note.NOTESPATH, '.index.sync'), 'wb') as fh:
            json.dump(fh, index)

    def _move(self, webdavConnection, src, dst):
        '''Move/Rename a note on webdav'''
        webdavConnection.path = self._get_notes_path()
        resource = webdavConnection.addResource(src)
        resource.move(self.webdavHost + self._get_notes_path() + dst)

    def _upload(self, webdavConnection, filename):
        #TODO set modification time on local file as it s not possible on remote
        print 'DEBUG: Upload', filename
        webdavConnection.path = self._get_notes_path()
        resource = webdavConnection.addResource(filename)
        fh = open(os.path.join(Note.NOTESPATH, filename), 'rb')
        resource.uploadFile(fh)
        fh.close()

    def _download(self, webdavConnection, filename):
        print 'DEBUG: Download', filename
        webdavConnection.path = self._get_notes_path() + filename
        #TODO manage conflict
        webdavConnection.downloadFile(os.path.join(Note.NOTESPATH, filename))
        #TODO set modification time on local

    def _remote_delete(self, webdavConnection, filename):
        #TODO
        print 'DEBUG: remote_delete', filename

    def _local_delete(self, filename):
        #TODO
        print 'DEBUG: locale_delete', filename

    def _unlock(self, filename):
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

    def _get_remote_filenames(self, webdavConnection):
        '''Check Remote Index'''
        webdavConnection.path = self._get_notes_path()
        index = dict([(basename(resource),
                        time.mktime(properties.getLastModified())) \
                        for (resource, properties) \
                        in webdavConnection.listResources().items()])
        print 'DEBUG _get_remote_filenames:', index
        return index

    def _get_local_filenames(self):
        print 'DEBUG 5:', Note.NOTESPATH
        index = dict([(filename,
                    os.path.getmtime(os.path.join(Note.NOTESPATH, filename)))
                    for filename in os.listdir(Note.NOTESPATH)
                    if os.path.isfile(os.path.join(Note.NOTESPATH, filename))])
        print 'DEBUG _get_local_filenames:', index
        return index

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