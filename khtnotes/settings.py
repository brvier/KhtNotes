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

import ConfigParser
from PySide.QtGui import QApplication
from PySide.QtCore import QUrl, Slot, QObject, Property, Signal
from PySide import QtDeclarative

import os

class Settings(QObject):
    '''Config object'''
    
    def __init__(self,):
        QObject.__init__(self,)
        self.config = ConfigParser.ConfigParser()
        if not os.path.exists(os.path.expanduser('~/.khtnotes.cfg')):
            self._write_default()
        else:
            self.config.read(os.path.expanduser('~/.khtnotes.cfg'))

    def _write_default(self):
        ''' Write the default config'''
        self.config.add_section('Display')
        self.config.set('Display', 'fontsize', '18')
        self.config.set('Display', 'fontfamily', 'Nokia Pure Text')
        self.config.add_section('Sync')
        self.config.set('Sync', 'url', 'https://khertan.net/khtnotes/sync.php')
        self.config.set('Sync', 'login', 'demo')
        self.config.set('Sync', 'password', 'demo')

        # Writing our configuration file to 'example.cfg'
        with open(os.path.expanduser('~/.khtnotes.cfg'), 'wb') as configfile:
            self.config.write(configfile)

    def _set(self,option, value):
        if option in ('url', 'login', 'password'):
          self.config.set('Sync',option, value)
        else:
          self.config.set('Display',option, value)

    @Slot(unicode, result=unicode)
    def get(self,option):
        try:
            return self.config.get('Display',option)
        except:
            try:
                return self.config.get('Display',option)
            except:
                return '' 

    def _get_fontSize(self,):
        return int(self.get('fontsize'))
    def _get_fontFamily(self,):
        return self.get('fontfamily')
    def _get_syncUrl(self,):
        return self.get('url')
    def _get_syncLogin(self,):
        return self.get('login')
    def _get_syncPassword(self,):
        return self.get('password')
    def _set_syncUrl(self, url):
        self._set('url', url)
    def _set_syncLogin(self, login):
        self._set('login', login)
    def _set_syncPassword(self, password):
        self._set('password', password)
 
    on_fontSize = Signal()
    on_fontFamily = Signal()
    on_syncUrl = Signal()
    on_syncLogin = Signal()
    on_syncPassword = Signal()

    fontSize = Property(int, _get_fontSize, notify=on_fontSize)
    fontFamily = Property(unicode, _get_fontFamily, notify=on_fontFamily)
    syncUrl = Property(unicode, _get_syncUrl, _set_syncUrl, notify=on_syncUrl)
    syncLogin = Property(unicode, _get_syncLogin, _set_syncLogin, notify=on_syncLogin)
    syncPassword = Property(unicode, _get_syncPassword, _set_syncPassword, notify=on_syncPassword)
