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

NOTESPATH = os.path.join(os.path.expanduser('~'), '.khtnotes')


class Settings(QObject):
    '''Config object'''

    def __init__(self,):
        QObject.__init__(self,)
        self.config = ConfigParser.ConfigParser()
        if not os.path.exists(os.path.expanduser('~/.khtnotes.cfg')):
            self._write_default()
        else:
            self.config.read(os.path.expanduser('~/.khtnotes.cfg'))
        if not self.config.has_section('Favorites'):
            self.config.add_section('Favorites')

        #Added in 2.19
        if not self.config.has_option('Webdav', 'remoteFolder'):
            self.config.set('Webdav', 'remoteFolder', 'Notes')
            #Remove local sync index to prevent losing notes :
            if os.path.exists(os.path.join(NOTESPATH, '.index.sync')):
                os.remove(os.path.join(NOTESPATH, '.index.sync'))

    def _write_default(self):
        ''' Write the default config'''
        self.config.add_section('Display')
        self.config.set('Display', 'fontsize', '18')
        self.config.set('Display', 'fontfamily', 'Nokia Pure Text')
        self.config.add_section('Webdav')
        self.config.set('Webdav', 'host', 'https://khertan.net/')
        self.config.set('Webdav', 'login', 'demo')
        self.config.set('Webdav', 'passwd', 'demo')
        self.config.set('Webdav', 'basePath',
                        '/remote.php/webdav/')
        self.config.set('Webdav', 'autoMerge', 'true')
        self.config.set('Webdav', 'remoteFolder', 'Notes')
        self.config.add_section('Favorites')

        # Writing our configuration file to 'example.cfg'
        with open(os.path.expanduser('~/.khtnotes.cfg'), 'wb') \
                as configfile:
            self.config.write(configfile)

    def _set(self, option, value):
        if option in ('host', 'login', 'passwd',
                      'basePath', 'autoMerge', 'remoteFolder'):
            self.config.set('Webdav', option, value)
            #Remove local sync index to prevent losing notes :
            if os.path.exists(os.path.join(NOTESPATH, '.index.sync')):
                os.remove(os.path.join(NOTESPATH, '.index.sync'))
        else:
            self.config.set('Display', option, value)

        self._write()

    def _write(self,):
        with open(os.path.expanduser('~/.khtnotes.cfg'), 'wb') \
                as configfile:
            self.config.write(configfile)

    @Slot(unicode)
    def add_favorite(self, uid):
        if not self.config.has_section("Favorites"):
            self.config.add_section("Favorites")
        self.config.set("Favorites", uid, 'True')
        self._write()

    @Slot(unicode)
    def remove_favorite(self, uid):
        try:
            self.config.remove_option("Favorites", uid)
            self._write()
        except KeyError:
            pass

    def is_favorited(self, uid):
        return (uid.lower() in self.get_favorites())

    def get_favorites(self):
        return self.config.options("Favorites")

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

    def _get_remoteFolder(self,):
        return self.get('remoteFolder')

    def _get_webdavPasswd(self,):
        return self.get('passwd')

    def _get_webdavBasePath(self,):
        return self.get('basePath')

    def _get_autoMerge(self,):
        return self.get('autoMerge') == 'true'

    def _set_autoMerge(self, b):
        return self._set('autoMerge', 'true' if b else 'false')

    def _set_webdavHost(self, url):
        self._set('host', url)

    def _set_remoteFolder(self, folder):
        self._set('remoteFolder', folder)

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
    on_remoteFolder = Signal()
    on_autoMerge = Signal()

    fontSize = Property(int, _get_fontSize, notify=on_fontSize)
    fontFamily = Property(unicode, _get_fontFamily,
                          notify=on_fontFamily)
    webdavHost = Property(unicode, _get_webdavHost,
                          _set_webdavHost, notify=on_webdavHost)
    webdavLogin = Property(unicode, _get_webdavLogin,
                           _set_webdavLogin, notify=on_webdavLogin)
    webdavPasswd = Property(unicode, _get_webdavPasswd,
                            _set_webdavPasswd, notify=on_webdavPasswd)
    webdavBasePath = Property(unicode, _get_webdavBasePath,
                              _set_webdavBasePath, notify=on_webdavBasePath)
    autoMerge = Property(bool, _get_autoMerge, _set_autoMerge,
                         notify=on_autoMerge)
    remoteFolder = Property(unicode, _get_remoteFolder, _set_remoteFolder,
                            notify=on_remoteFolder)
