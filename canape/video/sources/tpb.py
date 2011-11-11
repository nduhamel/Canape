#encoding:utf-8
#       tpb.py
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

import pytpb

from canape.video import torrent

class ThePirateBay(torrent.TorrentSearcher):
    """ Adaptater for pytpb the python API for The Pirate Bay"""
    
    name = 'The Pirate Bay'
    
    cat = { '1080p': 208,
            '720p': 208,
    }
    
    def __init__(self):
        self.tpb = pytpb.ThePirateBay()
    
    def search(self, term, quality=None):
        
        if quality:
            term = term + ' ' + quality
        
        cat = self.cat.get(quality, None)
        results = []
        
        for r in self.tpb.search(term, cat):
            results.append( self._process(r) )
        
        return results
    
    def _process(self, torrent):
        score = self._score(torrent)
        torrent = self._translate(torrent)
        torrent['torrent_score'] = score
        return torrent

    def _translate(self, torrent):
        """ translate a torrent dict from pytpb to a canonical torrent
        dict"""
        return { 'torrent_name': torrent['name'],
                 'torrent_size': torrent['size_of'],
                 'uploaded_date': torrent['uploaded_at'],
                 'torrent_url': torrent['torrent_url'],
                 'seeders': torrent['seeders'],
                 'leechers': torrent['leechers']
        }
    
    def _score(self, torrent):
        score = 0
        if torrent['user_type'] == 'VIP':
            score = 10
        elif torrent['user_type'] == 'trusted':
            score = 5
        return score
