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

logger = logging.getLogger(__name__)

import bencode
import transmissionrpc

from canape.downloader.torrent import TorrentDownloader

class Transmission(TorrentDownloader):
    name = 'transmission'
    
    def __init__(self, address=None, port=None, user=None, password=None):
        
        #Fallback to default
        address = address or 'localhost'
        port = port or 9091
                
        self.tc = transmissionrpc.Client(address, port=port, user=user, password=password)
    
    def addTorrent(self, videoObj):
        #Check torrent hash
        torrent = urllib.urlopen(videoObj.download_url).read()
        info = bencode.bdecode(torrent)['info']
        h = hashlib.sha1()
        h.update(bencode.bencode(info))
        torrentHash = h.hexdigest()
        torrents = [torrent.hashString for torrent in self.tc.list().values()]
        
        if torrentHash in torrents:
            logger.error("Can't add torrent '%s', it's already in downloading" % videoObj.name)
        else:
            self.tc.add_uri(videoObj.download_url)


if __name__ == '__main__':
    tc = Transmission()
    tc.addTorrent('coucou')
