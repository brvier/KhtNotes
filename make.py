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

from khtnotes import __version__, __upgrade__, __build__

__author__ = "Benoît HERVIER (khertan)"
__mail__ = "khertan@khertan.net"

if __name__ == "__main__":
    try:
        os.chdir(os.path.dirname(sys.argv[0]))
    except:
        pass
    p = pypackager.PyPackager("khtnotes")
    p.display_name = 'KhtNotes'
    p.version = __version__ + '.0'
    p.buildversion = __build__
    p.summary = 'A note taking application with ownCloud sync'
    p.description = "A note taking application for Harmattan devices" \
        + " (n950, n9), and Nemo Mobile/ MeeGo devices. KhtNotes provide" \
        + " sync of notes with ownCloud, and permit to previem markdown " \
        + "syntax"
    p.upgrade_description = __upgrade__
    p.author = __author__
    p.maintainer = __author__
    p.email = __mail__
    p.depends = "python, python-pyside.qtgui, python-pyside.qtdeclarative," \
        + " python-pyside.qtcore, python-pyside.qtopengl"
    p.rpm_depends = "python, python-pyside"
    p.suggests = ""
    p.section = "user/office"
    p.arch = "all"
    p.urgency = "low"
    p.icon = 'khtnotes.png'
    p.distribution = "harmattan"
    p.repository = "Khertan Repository"
    p.url = 'http://khertan.net/KhtNotes'
    p.bugtracker = 'http://github.com/khertan/KhtNotes/issues'
    p.changelog = p.upgrade_description
    p.maemo_flags = 'visible'
    p.meego_desktop_entry_filename = '/usr/share/applications/khtnotes.desktop'
    files = []
    p.postinst = '''#!/bin/sh
echo "Giving permissions for apps to execute"
chmod +x /opt/khtnotes/__init__.py
exit 0'''

    #Include byte compiled files, so do not remove it at packaging
    #time : selinux / obs spec packaging can require them
    from compileall import compile_dir
    compile_dir(os.path.join(os.path.dirname(__file__), p.name))
    os.system('python -O -m compileall '
              + os.path.join(os.path.dirname(__file__), p.name))

    #Src
    for root, dirs, fs in os.walk(os.path.join(os.path.dirname(__file__),
                                               p.name)):
        for f in fs:
            files.append(os.path.join(root, f))

    p['/usr/share/dbus-1/services'] = ['khtnotes.service', ]
    p['/usr/share/icons/hicolor/80x80/apps'] = ['khtnotes.png', ]
    p['/usr/share/icons/hicolor/64x64/apps'] = ['khtnotes_64.png', ]
    p['/usr/share/icons/hicolor/scalable/apps'] = ['khtnotes.svg', ]
    p['/usr/share/applications'] = ['khtnotes.desktop', ]
    p["/opt"] = files

    print p.generate(('debian_source', 'rpm_source', 'debian_binary'))
