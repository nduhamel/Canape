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

from canape.information.tvshow import TvShow

logger = logging.getLogger(__name__)

class Searcher:
    """ Interface to informations searcher objects 
    """
    
    def __init__(self):
        """ Load all search class"""
        path = os.path.dirname(__file__) + '/sources'
        self.sources_package = self._load_sources(path)
        self.tvshow_sources = [s() for s in TvShow.plugins]
    
    def get_seasons(self, seriename):
        """ Return list of seasons """
        return self.tvshow_sources[0].get_seasons(seriename)
        
    def get_episodes(self, seriename, snum):
        """ Return list of episodes """
        return self.tvshow_sources[0].get_episodes(seriename, snum)
    
    def get_airdate(self, seriename, snum, enum):
        """ Return airdate (datetime) """
        return self.tvshow_sources[0].get_airdate(seriename, snum, enum)
        
    def _load_sources(self, path):
        loaded = []
        for module_loader, name, ispkg in pkgutil.walk_packages(path=[path,]):
            logger.debug("Import: %s" % name)
            loaded.append( module_loader.find_module(name).load_module(name) )
        return loaded
