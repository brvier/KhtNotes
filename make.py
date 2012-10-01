#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Benoît HERVIER <khertan@khertan.net>
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
import sys
from glob import glob

import pypackager
sys.path.append('khtnotes')

from khtnotes import __version__, __upgrade__

__build__ = '1'
__author__ = "Benoît HERVIER (khertan)"
__mail__ = "khertan@khertan.net"

if __name__ == "__main__":
    try:
        os.chdir(os.path.dirname(sys.argv[0]))
    except:
        pass
    p=pypackager.PyPackager("khtnotes")
    p.display_name = 'KhtNotes'
    p.version = __version__+'.0'
    p.buildversion = __build__
    p.description="A note taking application for Harmattan devices (n950, n9). KhtNotes provide sync of notes with ownCloud, and permit to previem markdown syntax"
    p.upgrade_description=__upgrade__
    p.author=__author__
    p.maintainer=__author__
    p.email=__mail__
    p.depends = "python, python-pyside.qtgui, python-pyside.qtdeclarative, python-pyside.qtcore, python-pyside.qtopengl"
    p.suggests = ""
    p.section="user/office"
    p.arch="armel"
    p.urgency="low"
    p.icon='khtnotes.png'
    p.distribution="harmattan"
    p.repository="Khertan Repository"
    p.bugtracker = 'http://github.com/khertan/KhtNotes/issues'
    p.changelog =  p.upgrade_description
    p.maemo_flags = 'visible'
    p.meego_desktop_entry_filename = '/usr/share/applications/khtnotes.desktop'
    files = []
    p.postinst = '''#!/bin/sh
echo "Giving permissions for apps to execute"
chmod +x /opt/khtnotes/__init__.py
echo "Precompiling KhtNotes"
pycompile -O /opt/khtnotes/*.py
echo "Precompiling Webdav Lib"
pycompile -O /opt/khtnotes/webdav/*.py
exit 0'''
    p.prerm = '''#!/bin/sh
echo 'Removing compiled files'
rm -rf /opt/khtnotes/*.pyc
rm -rf /opt/khtnotes/webdav/*.pyc
rm -rf /opt/khtnotes/webdav/acp/*.pyc
rm -rf /opt/khtnotes/markdown/*.pyc
rm -rf /opt/khtnotes/markdown/extensions/*.pyc
exit 0'''

    p.createDigsigsums = True

    #Remove pyc and pyo
    for filepath in glob(os.path.join(os.path.dirname(__file__), p.name, '*.pyc')):
        os.remove(filepath)
    #Remove pyc and pyo
    for filepath in glob(os.path.join(os.path.dirname(__file__), p.name, '*.pyo')):
        os.remove(filepath)
    #Remove pyc and pyo
    for filepath in glob(os.path.join(os.path.dirname(__file__), p.name, 'webdav', '*.pyc')):
        os.remove(filepath)
    #Remove pyc and pyo
    for filepath in glob(os.path.join(os.path.dirname(__file__), p.name, 'webdav', '*.pyo')):
        os.remove(filepath)


    #Src
    for root, dirs, fs in os.walk(os.path.join(os.path.dirname(__file__), p.name)):
      for f in fs:
        files.append(os.path.join(root, f))

    p['/usr/share/dbus-1/services'] = ['khtnotes.service',]
    p['/usr/share/icons/hicolor/80x80/apps'] = ['khtnotes.png',]
    p['/usr/share/icons/hicolor/scalable/apps'] = ['khtnotes.svg',]
    p['/usr/share/applications'] = ['khtnotes.desktop',]
    p["/opt"] = files

    print p.generate(build_binary=True,build_src=True)
    if not os.path.exists('dists'):
        os.mkdir('dists')
    for filepath in glob(p.name+'_'+p.version+'-'+p.buildversion+'*'):
        os.rename(filepath, os.path.join(os.path.dirname(filepath), 'dists', os.path.basename(filepath)))
