#encoding:utf-8
#       subtitle/searcher.py
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

from canape.subtitle.tvshow import TvShowSubtitle

logger = logging.getLogger(__name__)


class Searcher:
    """ Interface to subtitle searcher objects 
    """
    
    def __init__(self):
        """ Load all search class"""
        path = os.path.dirname(__file__) + '/sources'
        self.sources_package = self._load_sources(path)
        self.tvshow_sources = [s() for s in TvShowSubtitle.plugins]

    def tvshow_search(self, tvshow, snum, enum, language):
        """ Return a list of found subtitle dicts """
        results = []
        for source in self.tvshow_sources:
            results.extend(source.search(tvshow, snum, enum, language))
        return results
    
    def _load_sources(self, path):
        loaded = []
        for module_loader, name, ispkg in pkgutil.walk_packages(path=[path,]):
            logger.debug("Import: %s" % name)
            loaded.append( module_loader.find_module(name).load_module(name) )
        return loaded
