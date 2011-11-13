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
import logging

import pytpb

from canape.video import tvshow
from canape.video import torrent

logger = logging.getLogger(__name__)


class ThePirateBay(torrent.TorrentSearcher, tvshow.TvShowSearcher):
    """ Adaptater for pytpb the python API for The Pirate Bay"""
    
    name = 'The Pirate Bay'
    
    cat_tvshow = { '1080p': 208,
            '720p': 208,
    }
    
    def __init__(self):
        self.tpb = pytpb.ThePirateBay()
    
    def tvshow_search(self, showname, snum, enum, quality=None):
        cat = self.cat_tvshow.get(quality, None)
        search_term='{0} S{1:0>2}E{2:0>2}'.format(showname, snum, enum)
        return self.search(search_term, quality, cat)

    def search(self, term, quality=None, cat=None):
        
        if quality:
            term = term + ' ' + quality
        logger.info("Search for '%s' in cat: %s" % (term, cat))
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
        return { 'type' : 'torrent',
                 'torrent_name': torrent['name'],
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
