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
import datetime

from canape.video import Searcher as Video
from canape.subtitle import Searcher as Subtitle
from canape.information import Searcher as Information
from canape.config import CanapeConfig
from canape.xmldb import Canapedb

logger = logging.getLogger(__name__)
    
class Canape(object):
    
    def __init__(self):
        
        self.config = CanapeConfig()
        self.db = Canapedb('testdb.xml')
        
        self.video = Video(self.config['sources'].as_list('video'))
        self.subtitle = Subtitle(self.config['sources'].as_list('subtitle'))
        self.information = Information(self.config['sources']['information'])
    
    def run(self):
        for serie in self.db.get_series():
            self.check(serie)
        
    
    def check(self, serie):
        todownload = []
        ep= self.information.get_episodes(serie['name'], serie['snum'])
        for ep in ep[serie['enum']:]:
            airdate = self.information.get_airdate(serie['name'], serie['snum'], ep)
            if airdate <= datetime.date.today():
                todownload.append( (serie['name'], serie['snum'], ep) )
        print todownload


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    canape = Canape()
    canape.run()

