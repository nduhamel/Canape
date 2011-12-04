#encoding:utf-8
#       logger.py
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
from canape.utils.log import dictConfig
from canape.config import CanapeConfig

__all__=[]

conf = CanapeConfig()

DEFAULT = {
    'version': 1,
    'disable_existing_loggers': True,

    'handlers': {
        'main': {
            'level': 'INFO',
            'class': 'canape.utils.log.FileHandler',
            'filename': 'canape.log'
        }
    },
    'loggers': {
        'canape': {
            'handlers':['main'],
            'propagate': True,
            'level':'INFO',
        },

        'canape.warning': {
            'handlers':['main'],
            'propagate': True,
            'level':'ERROR',
        },

    }
}

DEBUG = {
    'version': 1,
    'disable_existing_loggers': True,

    'handlers': {
        'main': {
            'level': 'DEBUG',
            'class': 'canape.utils.log.FileHandler',
            'filename': 'canape.log'
        }
    },
    'loggers': {
        'canape': {
            'handlers':['main'],
            'propagate': True,
            'level':'DEBUG',
        },

    }
}

AVALAIBLE = {'default':DEFAULT,
             'debug': DEBUG}

logmod = AVALAIBLE.get(conf['main']['logmode'], DEFAULT)

dictConfig(logmod)
