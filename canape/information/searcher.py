#encoding:utf-8
#       information/searcher.py
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
import os
import pkgutil
import logging

from canape.information.adapter_tvrage import TvRage

LOGGER = logging.getLogger(__name__)

class Searcher:
    """ Interface for informations searcher
    Based on tvrage api
    """

    def __init__(self):
        self.source = TvRage()

    def get_serie(self, name):
        """ get internal id of tv show"""
        return self.source.get_serie(name)

    def get_seasons(self, videoObj):
        """ Return list of seasons """
        return self.source.get_seasons(videoObj.name)

    def get_episodes(self, videoObj, snum):
        """ Return list of episodes """
        return self.source.get_episodes(videoObj.name, snum)

    def get_airdate(self, videoObj, snum, enum):
        """ Return airdate (datetime) """
        return self.source.get_airdate(videoObj.name, snum, enum)
