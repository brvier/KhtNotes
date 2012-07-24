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
from PySide.QtCore import Slot, QObject, Property, Signal

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
        self.config.add_section('Webdav')
        self.config.set('Webdav', 'host', 'https://khertan.net/')
        self.config.set('Webdav', 'login', 'demo')
        self.config.set('Webdav', 'passwd', 'demo')
        self.config.set('Webdav', 'basePath', '/owncloud/files/webdav.php')

        # Writing our configuration file to 'example.cfg'
        with open(os.path.expanduser('~/.khtnotes.cfg'), 'wb') as configfile:
            self.config.write(configfile)

    def _set(self, option, value):
        if option in ('host', 'login', 'password', 'basePath'):
            self.config.set('Webdav', option, value)
        else:
            self.config.set('Display', option, value)

        # Writing our configuration file to 'example.cfg'
        with open(os.path.expanduser('~/.khtnotes.cfg'), 'wb') as configfile:
            self.config.write(configfile)

    @Slot(unicode, result=unicode)
    def get(self, option):
        try:
            return self.config.get('Display', option)
        except:
            try:
                return self.config.get('Webdav', option)
            except:
                return ''

    def _get_fontSize(self,):
        return int(self.get('fontsize'))

    def _get_fontFamily(self,):
        return self.get('fontfamily')

    def _get_webdavHost(self,):
        return self.get('host')

    def _get_webdavLogin(self,):
        return self.get('login')

    def _get_webdavPasswd(self,):
        return self.get('passwd')

    def _get_webdavBasePath(self,):
        return self.get('basePath')

    def _set_webdavHost(self, url):
        self._set('host', url)

    def _set_webdavLogin(self, login):
        self._set('login', login)

    def _set_webdavPasswd(self, password):
        self._set('passwd', password)

    def _set_webdavBasePath(self, path):
        self._set('basePath', path)
    on_fontSize = Signal()
    on_fontFamily = Signal()
    on_webdavHost = Signal()
    on_webdavLogin = Signal()
    on_webdavPasswd = Signal()
    on_webdavBasePath = Signal()

    fontSize = Property(int, _get_fontSize, notify=on_fontSize)
    fontFamily = Property(unicode, _get_fontFamily, notify=on_fontFamily)
    webdavHost = Property(unicode, _get_webdavHost, \
                          _set_webdavHost, notify=on_webdavHost)
    webdavLogin = Property(unicode, _get_webdavLogin, \
                         _set_webdavLogin, notify=on_webdavLogin)
    webdavPasswd = Property(unicode, _get_webdavPasswd, \
                         _set_webdavPasswd, notify=on_webdavPasswd)
    webdavBasePath = Property(unicode, _get_webdavBasePath, \
                        _set_webdavBasePath, notify=on_webdavBasePath)
