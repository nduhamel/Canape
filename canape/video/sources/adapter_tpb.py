#encoding:utf-8
#       adapter_tpb.py
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
from canape.video.video import Video

LOGGER = logging.getLogger(__name__)

class ThePirateBay(tvshow.TvShowSearcher):
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
        LOGGER.info("Search for '%s' in cat: %s" % (term, cat))
        results = []
        for r in self.tpb.search(term, cat):
            results.append( self._process(r) )
        return results
    
    def _process(self, torrent):
        score = self._score(torrent)
        #Remove https to http
        return Video('torrent',torrent['name'], 'http://'+torrent['torrent_url'][8:],
                    size=torrent['size_of'], date=torrent['uploaded_at'],
                    sourcescore=score)
    
    def _score(self, torrent):
        score = torrent['seeders'] + torrent['leechers'] / 2
        if torrent['user_type'] == 'VIP':
            score += score * 0.1 #Add 10%
        elif torrent['user_type'] == 'trusted':
            score += score * 0.05 #Add 5%
        return score
