#!/usr/bin/python
# -a*- coding: utf-8 -*-
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

import unittest
import sys
import filecmp  # cmp
import os       # remove

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'khtnotes'))
import sync


class SyncTestCase(unittest.TestCase):
    ''' Test case of the sync with an ownCloud webdav
        yeah i know tests are horrible, require a webdav server with
        access configured in settings, and i should use mock
    '''
    def setUp(self, ):
        self.sync = sync.Sync()
        try:
            os.makedirs('/tmp/khtnotes_test/merge.sync/')
        except Exception:
            pass
        if os.name == 'nt':
            import tempfile
            self.sync._localDataFolder = os.path.join(tempfile.gettempdir(), u'khtnotes_test')
        else:
            self.sync._localDataFolder = u'/tmp/khtnotes_test'
        if not os.path.exists(self.sync._localDataFolder):
            os.makedirs(self.sync._localDataFolder)
        self.sync._remoteDataFolder = u'testKhtNotes2'
        self.webdavLogin, self.webdavPasswd, useAutoMerge = self.sync.readSettings()
        self.isConnected, self.webdavConnection, self.time_delta = self.sync.createConnection(
            self.webdavLogin,
            self.webdavPasswd)
        self.webdavConnection.path = self.sync.webdavBasePath
        self.sync._remoteDataFolder = u'testKhtNotes'  # Because it s rewritten by readSettings
        self.sync.logger.debug('WebdavConnection Path: %s : %s'
                               % (self.webdavConnection.path, self.sync._remoteDataFolder))
        if not self.webdavConnection.path + self.sync._remoteDataFolder + '/' in self.webdavConnection.listResources().keys():
            self.sync.logger.debug(self.webdavConnection.path + '/' + self.sync._remoteDataFolder)
            self.sync.logger.debug(self.webdavConnection.listResources().keys())
            self.webdavConnection.addCollection(self.sync._remoteDataFolder + '/')

    def tearDown(self,):
        import glob

        #Remove local
        for filename in glob.glob(os.path.join(self.sync._localDataFolder, '*')):
            try:  # remove only file
                os.remove(filename)
            except:
                pass

        #Remove remote
        remote_filenames = \
            self.sync._get_remote_filenames(self.webdavConnection)
        for filename in set(remote_filenames):
            self.sync._remote_delete(self.webdavConnection, filename)
        if self.sync._lock is not None:
            self.sync._unlock(self.webdavConnection)

    def test_check_khtnotes_folder_and_lock(self):
        #nosetests tests/SyncTestCase.py:SyncTestCase.test_check_khtnotes_folder_and_lock -s
        self.failUnless(self.sync._check_khtnotes_folder_and_lock(self.webdavConnection) is True)

    def test_LocalEdit(self):
        #self.cleanLocalAndRemote()
        #Create a file
        self.webdavConnection.path = self.sync._get_notes_path()
        self.sync._lock = self.webdavConnection.lockAll('KhtNotes', timeout='Second-300')

        lpath = os.path.join(self.sync._localDataFolder, 'testlocaledit.txt')
        with open(lpath, 'w') as fh:
            fh.write('1')
        #upload it
        self.sync._upload(self.webdavConnection, lpath, 'testlocaledit.txt', self.time_delta)
        #update it
        with open(lpath, 'w') as fh:
            fh.write('2')
        #sync
        #print self.webdavConnection.path
        self.sync._unlock(self.webdavConnection)
        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              True)
        #download it
        self.sync._download(self.webdavConnection, 'testlocaledit.txt', 'testlocaleditresult.txt',
                            self.time_delta)
        self.failUnless(filecmp.cmp(lpath,
                        os.path.join(self.sync._localDataFolder,
                        'testlocaleditresult.txt')), "File differs")
        #No need to test with/out autoMerge as it s not use here

    def test_RemoteEdit(self):
        #Create a file
        self.webdavConnection.path = self.sync._get_notes_path()
        self.sync._lock = self.webdavConnection.lockAll('KhtNotes', timeout='Second-300')

        with open(os.path.join(self.sync._localDataFolder, 'testremotedit1.txt'), 'w') as fh:
            fh.write('1')
        with open(os.path.join(self.sync._localDataFolder, 'testremotedit2.txt'), 'w') as fh:
            fh.write('2')
        #upload the modified one
        self.sync._upload(self.webdavConnection, os.path.join(self.sync._localDataFolder,
                                                              'testremotedit2.txt'),
                          'testremotedit1.txt',
                          self.time_delta)
        #remove the 2
        os.remove(os.path.join(self.sync._localDataFolder, 'testremotedit2.txt'))

        #sync
        #print self.webdavConnection.path
        self.sync._unlock(self.webdavConnection)
        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              True)
        #download it
        self.sync._download(
            self.webdavConnection,
            'testremotedit1.txt',
            'testremoteditresult.txt',
            self.time_delta)
        self.failUnless(
            filecmp.cmp(
                os.path.join(
                    self.sync._localDataFolder,
                    'testremotedit1.txt'),
                os.path.join(
                    self.sync._localDataFolder,
                    'testremoteditresult.txt')
            ), "File differs")
        #No need to test with/out autoMerge as it s not use here

    def test_ConflictEditWithMerge3(self):
        #self.cleanLocalAndRemote()
        self.webdavConnection.path = self.sync._get_notes_path()
        self.sync._lock = self.webdavConnection.lockAll('KhtNotes', timeout='Second-300')

        if not os.path.exists(os.path.join(self.sync._localDataFolder, 'merge.sync')):
            os.makedirs(os.path.join(self.sync._localDataFolder, 'merge.sync'))

        #Create a file
        with open(os.path.join(self.sync._localDataFolder, 'testmerge1.txt'), 'w') as fh:
            fh.write('1')
        with open(os.path.join(self.sync._localDataFolder, 'merge.sync', 'testmerge1.txt'), 'w') as fh:
            fh.write('1')

        #for merge3 we need a base
        with open(os.path.join(self.sync._localDataFolder, 'testmerge2.txt'), 'w') as fh:
            fh.write('2')

        #upload the modified one
        self.sync._upload(
            self.webdavConnection,
            os.path.join(
                self.sync._localDataFolder,
                'testmerge2.txt'
            ),
            'testmerge1.txt',
            self.time_delta)

        #remove the 2
        os.remove(os.path.join(self.sync._localDataFolder, 'testmerge2.txt'))
        with open(os.path.join(self.sync._localDataFolder, 'testmerge1.txt'), 'w') as fh:
            fh.write('3')

        #sync
        #print self.webdavConnection.path
        self.sync._unlock(self.webdavConnection)
        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              True)
        #download it
        self.sync._download(self.webdavConnection, 'testmerge1.txt', 'result.txt',
                            self.time_delta)

        #test result
        l = ''
        with open(os.path.join(self.sync._localDataFolder, 'testmerge1.txt'), 'r') as fh:
            l = fh.read()
        self.failUnless(l in ('32', '23'), "Incorrect local with Merge : %s" % l)
        l = ''
        with open(os.path.join(self.sync._localDataFolder, 'result.txt'), 'r') as fh:
            l = fh.read()
        self.failUnless(l in ('32', '23'), "Incorrect remote with Merge : %s" % l)

    def test_localDeleted(self):
        self.webdavConnection.path = self.sync._get_notes_path()
        self.sync._lock = self.webdavConnection.lockAll('KhtNotes', timeout='Second-300')

        with open(os.path.join(self.sync._localDataFolder, '1.txt'), 'w') as fh:
            fh.write('1')

        self.sync._upload(
            self.webdavConnection,
            os.path.join(
                self.sync._localDataFolder,
                '1.txt'
            ),
            '1.txt',
            self.time_delta)

        self.sync._unlock(self.webdavConnection)
        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              False)

        os.remove(os.path.join(self.sync._localDataFolder, '1.txt'))

        if not self.sync._lock is None:
            self.sync._unlock(self.webdavConnection)
        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              False)

        self.assertFalse(os.path.exists(os.path.join(self.sync._localDataFolder, '1.txt')),
                         "File still exists locally")
        self.webdavConnection.path = self.sync._get_notes_path()
        resources = [resource.path for resource, properties in self.webdavConnection.getCollectionContents()]
        self.assertFalse('1.txt' in resources, 'File still exits remotly')

    def test_remoteDeleted(self):
        self.webdavConnection.path = self.sync._get_notes_path()
        self.sync._lock = self.webdavConnection.lockAll('KhtNotes', timeout='Second-300')

        with open(os.path.join(self.sync._localDataFolder, '1.txt'), 'w') as fh:
            fh.write('1')

        self.sync._upload(
            self.webdavConnection,
            os.path.join(
                self.sync._localDataFolder,
                '1.txt'
            ),
            '1.txt',
            self.time_delta)

        self.sync._unlock(self.webdavConnection)
        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              False)

#        self.sync._lock = self.webdavConnection.lockAll('KhtNotes', timeout='Second-300')
        self.sync._remote_delete(self.webdavConnection, '1.txt')

        if not self.sync._lock is None:
            self.sync._unlock(self.webdavConnection)

        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              False)

        self.assertFalse(os.path.exists(os.path.join(self.sync._localDataFolder, '1.txt')),
                         "File still exists locally")
        self.webdavConnection.path = self.sync._get_notes_path()
        resources = [resource.path for resource, properties in self.webdavConnection.getCollectionContents()]
        self.assertFalse('1.txt' in resources, 'File still exits remotly')

    def test_ConflictEditWithoutMerge3(self):
        import time

        self.webdavConnection.path = self.sync._get_notes_path()
        self.sync._lock = self.webdavConnection.lockAll('KhtNotes', timeout='Second-300')

        #self.cleanLocalAndRemote()
        #Create a file
        with open(os.path.join(self.sync._localDataFolder, '1.txt'), 'w') as fh:
            fh.write('1')
        time.sleep(3)
        with open(os.path.join(self.sync._localDataFolder, '2.txt'), 'w') as fh:
            fh.write('2')
        #upload the modified one
        self.sync._upload(
            self.webdavConnection,
            os.path.join(
                self.sync._localDataFolder,
                '2.txt'
            ),
            '1.txt',
            self.time_delta)
        #remove the 2
        os.remove(os.path.join(self.sync._localDataFolder, '2.txt'))
        time.sleep(3)
        with open(os.path.join(self.sync._localDataFolder, '1.txt'), 'w') as fh:
            fh.write('3')

        #sync
        #print self.webdavConnection.path
        self.sync._unlock(self.webdavConnection)
        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              False)
        #download it
        self.sync._download(self.webdavConnection, '1.txt', 'result.txt',
                            self.time_delta)
        self.sync._download(self.webdavConnection, '1.Conflict.txt', 'result.Conflict.txt',
                            self.time_delta)
        self.failUnless(filecmp.cmp(os.path.join(self.sync._localDataFolder, '1.txt'),
                        os.path.join(self.sync._localDataFolder,
                        'result.txt')), "Original file isn't the same")
        self.failUnless(filecmp.cmp(os.path.join(self.sync._localDataFolder, '1.Conflict.txt'),
                        os.path.join(self.sync._localDataFolder,
                        'result.Conflict.txt')), "Conflicting file isn't the same")
        with open(os.path.join(self.sync._localDataFolder, '1.txt'), 'r') as fh:
            l = fh.read()
        self.assertTrue(l == '2', 'Incorrect Original file : %s' % l)
        with open(os.path.join(self.sync._localDataFolder, '1.Conflict.txt'), 'r') as fh:
            l = fh.read()
        self.assertTrue(l == '3', 'Incorrect Conflict file : %s' % l)

    def test_UploadDownload(self):

        self.webdavConnection.path = self.sync._get_notes_path()
        self.sync._lock = self.webdavConnection.lockAll('KhtNotes', timeout='Second-300')

        with open(self.sync._localDataFolder + '/local1.txt', 'w') as fh:
            fh.write('test file 1')

        self.sync._upload(self.webdavConnection,
                          os.path.join(self.sync._localDataFolder,
                                       'local1.txt'),
                          'remote1.txt', self.time_delta)
        self.sync._download(self.webdavConnection, 'remote1.txt',
                            'result1.txt', self.time_delta)

        self.failUnless(
            filecmp.cmp(
                os.path.join(
                    self.sync._localDataFolder,
                    'result1.txt'
                ),
                os.path.join(
                    self.sync._localDataFolder,
                    'local1.txt')
            ), "File differs")
