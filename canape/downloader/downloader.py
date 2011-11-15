#encoding:utf-8
#       downloader/downloader.py
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

from canape.downloader.torrent import TorrentDownloader

logger = logging.getLogger(__name__)

class Downloader(object):
    """ Interface to downloader objects 
    """
    
    def __init__(self, config, used=None):
        """ Load all search class"""
        path = os.path.dirname(__file__) + '/adapters'
        self.sources_package = self._load_downloaders(path, used)
        
        self.torrent_downloaders=[]
        for d in TorrentDownloader.plugins:
            if d.name in config.keys():
                self.torrent_downloaders.append( d(**config[d.name]) )
            else:
                self.torrent_downloaders.append(d())
        
        logger.debug("Available torrent downloaders: %s" % self.torrent_downloaders)
    
    def addVideo(self, videoObj):
        self.torrent_downloaders[0].addTorrent(videoObj)
    
    def _load_downloaders(self, path, used=None):
        loaded = []
        for module_loader, name, ispkg in pkgutil.walk_packages(path=[path,]):
            if used == None:
                logger.debug("All import: %s" % name[8:])
                loaded.append( module_loader.find_module(name).load_module(name) )
            elif name[8:] in used:
                logger.debug("Import specified downloader: %s" % name[8:])
                loaded.append( module_loader.find_module(name).load_module(name) )
        return loaded
