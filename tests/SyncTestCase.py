import unittest
import sys
import filecmp  # cmp
import os       # remove
import getopt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'khtnotes'))
import sync

class SyncTestCase(unittest.TestCase):
    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self.sync = sync.Sync()
        try:
            os.mkdir('/tmp/khtnotes_test/')
        except:
            pass
        self.sync._localDataFolder = '/tmp/khtnotes_test'
        self.sync._remoteDataFolder = 'testKhtNotes'
        self.webdavLogin, self.webdavPasswd, useAutoMerge = self.sync.readSettings()
        self.isConnected, self.webdavConnection, self.time_delta = self.sync.createConnection(self.webdavLogin, self.webdavPasswd)

    def testLocalEdit(self):
        #Create a file
        lpath = os.path.join(self.sync._localDataFolder , '1.txt')
        with open(lpath, 'w') as fh:
            fh.write('1')
        #upload it
        self.sync._upload(self.webdavConnection, lpath, '1.txt', self.time_delta)
        #update it
        with open(lpath, 'w') as fh:
            fh.write('2')
        #sync
        self.sync._sync_files(self.webdavConnection,
                              self.time_delta,
                              True)
        #download it
        self.sync._download(self.webdavConnection, '1.txt', 'result.txt',
                            self.time_delta)
        self.failUnless(filecmp.cmp(lpath,
            os.path.join(self.sync._localDataFolder,
            'result.txt')), "File differs")

        #No need to test with/out autoMerge as it s not use here

    def testUploadDownload(self):
        with open (self.sync._localDataFolder + '/local1.txt', 'w') as fh:
            fh.write('test file 1')

        self.sync._upload(self.webdavConnection,
                          os.path.join(self.sync._localDataFolder,
                                       'local1.txt'),\
                          'remote1.txt', self.time_delta)
        self.sync._download(self.webdavConnection, 'remote1.txt', \
                            'result1.txt', self.time_delta)

        self.failUnless(filecmp.cmp(os.path.join(self.sync._localDataFolder, 'result1.txt'), os.path.join(self.sync._localDataFolder, 'local1.txt')), "File differs")

class SyncTestSuite(unittest.TestSuite):
    def __init__(self, methods):
        unittest.TestSuite.__init__(self, map(SyncTestCase, methods))

if  __name__ == '__main__':
    methodNames= ("testUploadDownload",
                  "testLocalEdit",
                )

    suite= SyncTestSuite(methodNames)
    unittest.TextTestRunner().run(suite)
