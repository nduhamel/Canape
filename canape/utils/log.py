#encoding:utf-8
#       utils/log.py
#
#       Copyright 2011 nicolas <nicolas@jombi.fr>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
import logging
import warnings

import canape.env

__all__ = ['dictConfig', 'NullHandler', 'RotatingFileHandler']

# Make sure that dictConfig is available
# This was added in Python 2.7/3.2
try:
    from logging.config import dictConfig
except ImportError:
    from canape.utils.dictconfig import dictConfig

# Make sure a NullHandler is available
# This was added in Python 2.7/3.2
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Wrap FileHandler to keep track of opened files
# Usefull for daemon mode
class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, **kwargs):
        canape.env.OPEN_FILES.append(kwargs.get('filename'))
        kwargs.setdefault('maxBytes',1048576)
        kwargs.setdefault('backupCount',5)
        logging.handlers.RotatingFileHandler.__init__(self,**kwargs)

# Ensure the creation of the canape logger
# with a null handler. This ensures we don't get any
# 'No handlers could be found for logger "canape"' messages
logger = logging.getLogger('canape')
if not logger.handlers:
    logger.addHandler(NullHandler())



# Redirect warning to logger canape.warning
def customwarn(message, category, filename, lineno, file=None, line=None):
    logger = logging.getLogger('canape.warning')
    logger.warning(warnings.formatwarning(message, category, filename, lineno))

warnings.showwarning = customwarn
