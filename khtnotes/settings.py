#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Benoit HERVIER <khertan@khertan.net>
# Licenced under GPLv3

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import ConfigParser
from PySide.QtCore import Slot, QObject, Property, Signal

import os

NOTESPATH = os.path.join(os.path.expanduser(u'~'), u'.khtnotes')


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
            self._write()

        # Added in 2.19
        if not self.config.has_option('Webdav', 'remoteFolder'):
            self.config.set('Webdav', 'remoteFolder', 'Notes')
            self._write()
            # Remove local sync index to prevent losing notes :
            if os.path.exists(os.path.join(NOTESPATH, '.index.sync')):
                os.remove(os.path.join(NOTESPATH, '.index.sync'))

        # Added in 2.20
        if not self.config.has_option('Display', 'displayHeader'):
            self.config.set('Display', 'displayHeader', 'true')
            self._write()

        # Added in 3.0
        if not self.config.has_option('Keyboard', 'hideVkb'):
            self.config.add_section('Keyboard')
            self.config.set('Keyboard', 'hideVkb', 'true')
            self._write()

        if not self.config.has_option('Webdav', 'autoSync'):
            self.config.set('Webdav', 'autoSync', 'false')
            self._write()

        if not self.config.has_section('Scriptogram'):
            self.config.add_section('Scriptogram')
            self.config.set('Scriptogram', 'userid', '')

    def _write_default(self):
        ''' Write the default config'''
        self.config.add_section('Display')
        self.config.set('Display', 'fontsize', '18')
        self.config.set('Display', 'fontfamily', 'Nokia Pure Text')
        self.config.set('Display', 'displayHeader', 'true')
        self.config.add_section('Webdav')
        self.config.set('Webdav', 'host', 'https://khertan.net/')
        self.config.set('Webdav', 'login', 'demo')
        self.config.set('Webdav', 'passwd', 'demo')
        self.config.set('Webdav', 'basePath',
                        '/remote.php/webdav/')
        self.config.set('Webdav', 'autoMerge', 'true')
        self.config.set('Webdav', 'remoteFolder', 'Notes')
        self.config.set('Webdav', 'autoSync', 'false')
        self.config.add_section('Keyboard')
        self.config.set('Keyboard', 'hideVkb', 'false')
        self.config.add_section('Favorites')
        self.config.add_section('Scriptogram')
        self.config.set('Scriptogram', 'userid', '')

        # Writing our configuration file to 'example.cfg'
        with open(os.path.expanduser('~/.khtnotes.cfg'), 'wb') \
                as configfile:
            self.config.write(configfile)

    def _set(self, option, value):
        # Avoid useless change due to binding
        if self.get(option) == value:
            return

        if option in ('host', 'login', 'passwd',
                      'basePath', 'autoMerge', 'remoteFolder',
                      'autoSync'):
            self.config.set('Webdav', option, value)
            # Remove local sync index to prevent losing notes :
            if os.path.exists(os.path.join(NOTESPATH, '.index.sync')):
                os.remove(os.path.join(NOTESPATH, '.index.sync'))
        elif option in ('hideVkb'):
            self.config.set('Keyboard', option, value)
        elif option in ('userid'):
            self.config.set('Scriptogram', option, value)
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
            return self.config.get('Keyboard', option)
        except:
            try:
                return self.config.get('Display', option)
            except:
                try:
                    return self.config.get('Webdav', option)
                except:
                    try:
                        return self.config.get('Scriptogram', option)
                    except:
                        return ''

    def _get_fontSize(self, ):
        return int(self.get('fontsize'))

    def _set_fontSize(self, value):
        self._set('fontsize', unicode(value))
        self.on_fontSize.emit()

    def _get_displayHeader(self):
        return self.get('displayheader') == 'true'

    def _set_displayHeader(self, b):
        self._set('displayheader', 'true' if b else 'false')
        self.on_displayHeader.emit()

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
        self._set('autoMerge', 'true' if b else 'false')

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

    def _get_hideVkb(self,):
        return self.get('hideVkb') == 'true'

    def _set_hideVkb(self, b):
        return self._set('hideVkb', 'true' if b else 'false')

    def _get_autoSync(self,):
        return self.get('autoSync') == 'true'

    def _set_autoSync(self, b):
        return self._set('autoSync', 'true' if b else 'false')

    def _get_scriptogramuserid(self,):
        return self.get('userid')

    def _set_scriptogramuserid(self, value):
        return self._set('userid', value)

    on_fontSize = Signal()
    on_fontFamily = Signal()
    on_webdavHost = Signal()
    on_webdavLogin = Signal()
    on_webdavPasswd = Signal()
    on_webdavBasePath = Signal()
    on_remoteFolder = Signal()
    on_autoMerge = Signal()
    on_displayHeader = Signal()
    on_hideVkb = Signal()
    on_autoSync = Signal()
    on_scriptogramUserId = Signal()

    scriptogramUserId = Property(unicode,
                                 _get_scriptogramuserid,
                                 _set_scriptogramuserid,
                                 notify=on_scriptogramUserId)
    autoSync = Property(bool, _get_autoSync,
                        _set_autoSync, notify=on_autoSync)
    hideVkb = Property(bool, _get_hideVkb,
                       _set_hideVkb, notify=on_hideVkb)
    fontSize = Property(int, _get_fontSize,
                        _set_fontSize, notify=on_fontSize)
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
    displayHeader = Property(bool, _get_displayHeader, _set_displayHeader,
                             notify=on_displayHeader)
    remoteFolder = Property(unicode, _get_remoteFolder, _set_remoteFolder,
                            notify=on_remoteFolder)
