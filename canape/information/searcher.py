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

    def get_serie_id(self, seriename):
        return self.source.get_serie_id(seriename)

    def get_seasons(self, seriename):
        """ Return list of seasons """
        return self.source.get_seasons(seriename)

    def get_episodes(self, seriename, snum):
        """ Return list of episodes """
        return self.source.get_episodes(seriename, snum)

    def get_airdate(self, seriename, snum, enum):
        """ Return airdate (datetime) """
        return self.source.get_airdate(seriename, snum, enum)
