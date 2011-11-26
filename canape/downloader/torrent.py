#encoding:utf-8
#       downloader/torrent.py
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

import bencode

from canape.utils import PluginMount

class TorrentDownloader:
    """ Base object for torrent downloader """
    __metaclass__ = PluginMount

    def addTorrent(self, videoObj):
        raise NotImplementedError()


def compute_hash(videoObj):
    """ Return torrent hash """
    torrent = urllib.urlopen(videoObj.download_url).read()
    info = bencode.bdecode(torrent)['info']
    h = hashlib.sha1()
    h.update(bencode.bencode(info))
    return h.hexdigest()
