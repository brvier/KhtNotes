# Copyright 2008 German Aerospace Center (DLR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#Module from the libwebdav module

""""
Module provides access to a configured logger instance.
The logger writes C{sys.stdout}.
"""

import logging
import sys


_defaultLoggerName = "KhtNotes"
_fileLogFormat = "%(asctime)s: %(levelname)s: %(message)s"


def getDefaultLogger(handler=None):
    """
    Returns a configured logger object.

    @return: Logger instance.
    @rtype: C{logging.Logger}
    """

    myLogger = logging.getLogger(_defaultLoggerName)
    if len(myLogger.handlers) == 0:
        myLogger.level = logging.DEBUG
        formatter = logging.Formatter(_fileLogFormat)
        if handler is None:
            stdoutHandler = logging.StreamHandler(sys.stdout)
            stdoutHandler.setFormatter(formatter)
            myLogger.addHandler(stdoutHandler)
        else:
            myLogger.addHandler(handler)
    return myLogger 