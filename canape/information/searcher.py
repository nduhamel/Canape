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

LOGGER = logging.getLogger(__name__)

class Searcher:
    """ Interface to informations searcher objects 
    """
    
    def __init__(self, used_source=None):
        """ Load all search class"""
        path = os.path.dirname(__file__) + '/sources'
        self.sources_package = self._load_sources(path, used_source)
        available_tvshow_sources = [s() for s in TvShow.plugins]
        if len(available_tvshow_sources) == 0:
            if used_source == None:
                pass #Raise an error "no available sources"
            else:
                pass #Raise an error "Source: %s not found"
        else:
            self.source = available_tvshow_sources[0]            
    
    def get_seasons(self, seriename):
        """ Return list of seasons """
        return self.source.get_seasons(seriename)
        
    def get_episodes(self, seriename, snum):
        """ Return list of episodes """
        return self.source.get_episodes(seriename, snum)
    
    def get_airdate(self, seriename, snum, enum):
        """ Return airdate (datetime) """
        return self.source.get_airdate(seriename, snum, enum)
        
    def _load_sources(self, path, used_source=None):
        loaded = []
        for module_loader, name, ispkg in pkgutil.walk_packages(path=[path,]):
            if used_source == None:
                LOGGER.debug("All import: %s" % name[8:])
                loaded.append( module_loader.find_module(name).load_module(name) )
            elif name[8:] == used_source:
                LOGGER.debug("Import specified source: %s" % name[8:])
                loaded.append( module_loader.find_module(name).load_module(name) )
        return loaded
