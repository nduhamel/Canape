#encoding:utf-8
#       adapter_transmission.py
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

import transmissionrpc

from canape.downloader.torrent import TorrentDownloader, compute_hash
from canape.exceptions import InvalidConfig
from canape.downloader.exceptions import RemoteSoftwareUnavailable, AlreadyDownloading, UnknownDownload

LOGGER = logging.getLogger(__name__)

class Transmission(TorrentDownloader):
    name = 'transmission'

    def __init__(self, address=None, port=None, user=None, password=None, download_dir=None):

        self.download_dir = download_dir

        #Fallback to default
        address = address or 'localhost'
        port = port or 9091

        try:
            self.tc = transmissionrpc.Client(address, port=port, user=user, password=password)
        except transmissionrpc.TransmissionError as e:
            if isinstance(e.original, transmissionrpc.HTTPHandlerError):
                if e.original.code == 111:
                    raise RemoteSoftwareUnavailable('Transmission not started or invalid connection options: %s:%s ' % (address,port))
                elif e.original.code == 401:
                    raise InvalidConfig('TransmissionRPC config invalid user:%s password:%s' % (user,password))
            raise

    def addTorrent(self, videoObj):
        """ Add a torrent to transmission and return torrent hash as id"""
        torrents_hash = [torrent.hashString for torrent in self.tc.list().values()]
        if compute_hash(videoObj) in torrents_hash:
            raise AlreadyDownloading("Torrent already in download")
        else:
            if self.download_dir is not None:
                self.tc.add_uri(videoObj.download_url, download_dir=self.download_dir)
            else:
                self.tc.add_uri(videoObj.download_url)

    def is_finished(self, torrent_hash):
        info = self.tc.info(torrent_hash)
        if not info:
            raise UnknownDownload()
        if info.values()[0].progress == 100:
            return True
        else:
            return False
