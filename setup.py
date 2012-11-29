#!/usr/bin/python
# -*- coding: utf-8 -*-

#KhtNotes Setup File
import khtnotes
import sys
reload(sys).setdefaultencoding("UTF-8")

from distutils.core import setup


#Remove temporary files
for root, dirs, fs in os.walk(os.path.join(os.path.dirname(__file__),
                                           p.name)):
    for filename in [filename for filename
                     in fs if filename.endswith(('~', '.pyo', '.pyc', ))]:
        files.append(os.path.join(root, filename))


setup(name='khteditor',
      version=khtnotes.__version__,
      license='GNU GPLv3',
      description='A note taking application with ownCloud sync',
      long_description="A note taking application for Harmattan devices"
                       + " (n950, n9), and Nemo Mobile/ MeeGo devices. "
                       + "KhtNotes provide"
                       + " sync of notes with ownCloud, "
                       + "and permit to preview markdown syntax",
      author=u'Benoît HERVIER',
      author_email='khertan@khertan.net',
      maintainer=u'Benoît HERVIER',
      maintainer_email='khertan@khertan.net',
      url='http://www.khertan.net/KhtNotes',
      requires=['python', 'python-pyside'],
      packages=['khtnotes', ],
      package_data={'khtnotes': ['icons/*',
                                 'qml/components/*',
                                 'qml/*.js',
                                 'qml/*.qml'], },
      data_files=[('/usr/share/dbus-1/services', ['khtnotes.service']),
                  ('/usr/share/applications/', ['khtnotes.desktop']),
                  ('/usr/share/icons/hicolor/80x80/apps', ['khtnotes.png']),
                  ('/usr/share/icons/hicolor/64x64/apps', ['khtnotes_64.png']),
                  ('/usr/share/icons/hicolor/scalable/apps', ['khtnotes.svg']),
                  ],
      scripts=[],
      'bdist_rpm': {
      'requires': 'python, python-pyside',
      'icon': 'khtnotes.png',
      'group': 'Office', }}
     )

