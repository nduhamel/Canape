#encoding:utf-8
#       main.py
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
"""
Try to watch for new episodes and download them
dep:
 python-tvrage
 pytpb              https://github.com/nduhamel/pytpb
 tvsubtitles_api    https://github.com/nduhamel/tvsubtitles_api
 
 //bencode            http://pypi.python.org/pypi/bencode/  for .torrent decode
"""
import datetime
import logging

import tvrage.api

import canape.video
import canape.subtitle
import canape.information

logger = logging.getLogger(__name__)

def search_for_new_episodes(seriename, season, lastviewed):
    """ Return list of next episodes, episodes are dict:
    keys: sname, ename, enum, snum, airdate"""
    
    show = tvrage.api.Show(seriename)
    season = show.season(season)
    next_ep = season.keys()[lastviewed:]
    data = []
    for ep in next_ep:
        e = {}
        e['sname'] = show.name
        e['ename'] = season[ep].title
        e['enum'] = season[ep].number
        e['snum'] = season[ep].season
        e['airdate'] = season[ep].airdate
        data.append(e)
    return data

def is_already_aired(ep):
    """ take an episode dict like them returned by 
    search_for_new_episodes() and return True if
    it have been already aired
    """
    return ep['airdate'] <= datetime.date.today()
    

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    
    tvsearcher = canape.video.searcher.Searcher()
    subsearcher = canape.subtitle.searcher.Searcher()
    information = canape.information.searcher.Searcher()
    
    for r in tvsearcher.tvshow_search('the walking dead', 2, 3, '720p'):
        print r['torrent_name']
