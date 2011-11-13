#encoding:utf-8
#       information/sources/tvrage.py
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
import datetime

import tvrage.api

from canape.information.tvshow import TvShow

class TvRage(TvShow):
    """ Adapter for Tvrage api """ 
    
    def __init__(self):
        self._shows =  {}
        
    def get_seasons(self, seriename):
        """ Return list of seasons """
        if seriename not in self._shows.keys():
            self._get_serie(seriename)
        return range(1, self._shows[seriename].seasons +1)
        
    def get_episodes(self, seriename, snum):
        """ Return list of episodes """
        if seriename not in self._shows.keys():
            self._get_serie(seriename)
        return self._shows[seriename].season(snum).keys()

    def get_airdate(self, seriename, snum, enum):
        """ Return airdate (datetime) """
        if seriename not in self._shows.keys():
            self._get_serie(seriename)
        return self._shows[seriename].season(snum)[enum].airdate
    
    def _get_serie(self, seriename):
        self._shows[seriename] = tvrage.api.Show(seriename)    
