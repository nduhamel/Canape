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
 python-tvrage      http://pypi.python.org/pypi/python-tvrage/
 pytpb              https://github.com/nduhamel/pytpb
 tvsubtitles_api    https://github.com/nduhamel/tvsubtitles_api
 configobj      
 //bencode            http://pypi.python.org/pypi/bencode/  for .torrent decode
"""
import logging

import canape.video
import canape.subtitle
import canape.information
import canape.config

logger = logging.getLogger(__name__)
    

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    
    config = canape.config.CanapeConfig()
    
    tvsearcher = canape.video.searcher.Searcher(config['sources'].as_list('video'))
    subsearcher = canape.subtitle.searcher.Searcher(config['sources'].as_list('subtitle'))
    information = canape.information.searcher.Searcher(config['sources']['information'])
