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

from canape.exceptions import CanapeException
from canape.downloader.torrent import TorrentDownloader

LOGGER = logging.getLogger(__name__)

class Downloader(object):
    """ Interface to downloader objects 
    """
    
    def __init__(self, config, used=None):
        """ Load all search class"""
        self.config = config
        path = os.path.dirname(__file__) + '/adapters'
        self.sources_package = self._load_downloaders(path, used)
        
        self.torrent_downloaders=[]
        for d in TorrentDownloader.plugins:
            try:
                if d.name in config['adapters'].keys():
                    self.torrent_downloaders.append( d(**config['adapters'][d.name]) )
                else:
                    self.torrent_downloaders.append(d())
            except CanapeException as e:
                LOGGER.error("Adapter:%s Error:%s" %(d.name,e))
                
        if len(self.torrent_downloaders):
            LOGGER.debug("Available torrent downloaders: %s" % self.torrent_downloaders)
        else:
            LOGGER.error('No available torrent downloaders')
    
    def addVideo(self, videoObj):
        self.torrent_downloaders[0].addTorrent(videoObj)
    
    def addSubtitle(self, subtitleObj):
        destname = self.config['download_dir']+'/'+subtitleObj.name+'.str'
        with open(destname, 'w') as f:
            f.write(subtitleObj.getFile().read())
    
    def _load_downloaders(self, path, used=None):
        loaded = []
        for module_loader, name, ispkg in pkgutil.walk_packages(path=[path,]):
            if used == None:
                LOGGER.debug("All import: %s" % name[8:])
                loaded.append( module_loader.find_module(name).load_module(name) )
            elif name[8:] in used:
                LOGGER.debug("Import specified downloader: %s" % name[8:])
                loaded.append( module_loader.find_module(name).load_module(name) )
        return loaded
