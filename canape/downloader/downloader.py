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
from canape.downloader.torrent import TorrentDownloader, compute_hash
from canape.downloader.downloadqueue import DownloadQueue, AlreadyExist
from canape.downloader.exceptions import UnknownDownload, AlreadyDownloading

LOGGER = logging.getLogger(__name__)

class Downloader(object):
    """ Interface to downloader objects
    """

    def __init__(self, config, used=None):
        """ Load all search class"""
        self.config = config
        path = os.path.dirname(__file__) + '/adapters'
        self.sources_package = self._load_downloader_modules(path, used)
        self.queue = DownloadQueue(self.config['DOWNLOADS_DB'])
        self.torrent_downloaders=[]
        self._load_torrent_downloaders()
        if len(self.torrent_downloaders):
            LOGGER.info("Available torrent downloaders: %s" % "; ".join([t.name for t in self.torrent_downloaders]) )
        else:
            LOGGER.error('No available torrent downloaders')

    def addVideo(self, videoObj):
        if videoObj.vtype == 'torrent':
            self._add_torrent(videoObj)
        else:
            raise TypeError()

    def check(self):
        """ Used for check downloader and retry to download """
        if len(self.torrent_downloaders) == 0:
            self._load_torrent_downloaders

        if len(self.torrent_downloaders):
            try:
                while True:
                    download = self.queue.pop()
                    LOGGER.info("Start download of: %s" % download.name)
                    self.addVideo(download)
            except IndexError:
                pass

    def is_finished(self, videoid):
        """ check if a video is downloading """
        for download in self.queue:
            if download.id_ == videoid:
                if download.extra['state'] == self.queue.WAITING:
                    return False
                isfinished = False
                try:
                    isfinished = self.torrent_downloaders[0].is_finished(download.extra['downloader_id'])
                except UnknownDownload:
                    self.queue.remove(download.id_)
                    LOGGER.error("Download %s unknown delete it from queue" % download.name)
                    raise
                if isfinished:
                    LOGGER.debug("Download %s finished delete it from queue" % download.name)
                    self.queue.remove(download.id_)
                return isfinished
        raise UnknownDownload("Downloader have no trace of this download")

    def _add_torrent(self, videoObj):
        if len(self.torrent_downloaders):
            try:
                self.torrent_downloaders[0].addTorrent(videoObj)
            except AlreadyDownloading:
                LOGGER.error("Download %s already downloading" % videoObj)
            videoObj.extra['downloader_id'] = compute_hash(videoObj)
            try:
                self.queue.append(videoObj, self.queue.STARTED)
            except AlreadyExist:
                LOGGER.error("Download %s already in download queue" % videoObj)
        else:
            LOGGER.warning('No available downloader, put in queue')
            try:
                self.queue.append(videoObj)
            except AlreadyExist:
                LOGGER.error("Download %s already in download queue" % videoObj)

    def addSubtitle(self, subtitleObj):
        destname = self.config['download_dir']+'/'+subtitleObj.name+'.str'
        with open(destname, 'w') as f:
            f.write(subtitleObj.getFile().read())

    def _load_downloader_modules(self, path, used=None):
        loaded = []
        for module_loader, name, ispkg in pkgutil.walk_packages(path=[path,]):
            if used == None:
                LOGGER.debug("All import: %s" % name[8:])
                loaded.append( module_loader.find_module(name).load_module(name) )
            elif name[8:] in used:
                LOGGER.debug("Import specified downloader: %s" % name[8:])
                loaded.append( module_loader.find_module(name).load_module(name) )
        return loaded

    def _load_torrent_downloaders(self):
        """ Load torrent downloaders """
        for d in TorrentDownloader.plugins:
            try:
                if d.name in self.config['adapters'].keys():
                    self.torrent_downloaders.append( d(**self.config['adapters'][d.name]) )
                else:
                    self.torrent_downloaders.append(d())
            except CanapeException as e:
                LOGGER.error("Adapter:%s Error:%s" %(d.name,e))
