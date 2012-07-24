"""
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
