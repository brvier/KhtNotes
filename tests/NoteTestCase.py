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
import note

class NoteTestCase(unittest.TestCase):
    ''' Test case of the sync with an ownCloud webdav
        yeah i know tests are horrible, require a webdav server with
        access configured in settings, and i should use mock
    '''
    def setUp(self, ):
        self.note = note.Note()

    def tearDown(self,):
        pass

    def test_ColorizeAndUncolorize(self, ):
        original = '''
Test
----
test test **test** test *test*
* *test*
**test**
* test
  * test
* test
test
====
test'''

        result='''<html><body><big><font color="#663366">Test<br>
----</font></big><br>
test test <b>**test**</b> test <i>*test*</i><br>
<i>* *</i>test*<br>
<b>**test**</b><br>
* test<br>
  * test<br>
* test<br>
<big><font color="#441144">test<br>
====</font></big><br>
test</body></html>'''.replace('\n', '')
        self.assertEqual(note._colorize(original), result)
        self.assertEqual(original[1:], note._uncolorize(result))
        self.assertEqual(note._colorize(original[1:]), note._colorize(note._uncolorize(result)))
