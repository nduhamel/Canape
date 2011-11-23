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
import urllib
import hashlib
import logging

LOGGER = logging.getLogger(__name__)

import bencode
import transmissionrpc

from canape.downloader.torrent import TorrentDownloader
from canape.exceptions import InvalidConfig
from canape.downloader.exceptions import RemoteSoftwareUnavailable, AlreadyDownloading, UnknownDownload


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
        #Check torrent hash
        torrent = urllib.urlopen(videoObj.download_url).read()
        info = bencode.bdecode(torrent)['info']
        h = hashlib.sha1()
        h.update(bencode.bencode(info))
        torrentHash = h.hexdigest()
        torrents = [torrent.hashString for torrent in self.tc.list().values()]

        if torrentHash in torrents:
            raise AlreadyDownloading("Torrent already in download")
        else:
            if self.download_dir is not None:
                torrent = self.tc.add_uri(videoObj.download_url, download_dir=self.download_dir)
            else:
                torrent = self.tc.add_uri(videoObj.download_url)
            return str(torrent.keys()[0])

    def is_finished(self, torrentid):
        torrentid = int(torrentid)
        info = self.tc.info(torrentid)
        if not info:
            raise UnknownDownload()

        if info[torrentid].progress == 100:
            return True
        else:
            return False

if __name__ == '__main__':
    tc = Transmission()
    tc.addTorrent('coucou')
