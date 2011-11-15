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
from canape.chooser import VideoChooser

logger = logging.getLogger(__name__)
    
class Canape(object):
    
    def __init__(self):
        
        self.config = CanapeConfig()
        self.db = Canapedb('testdb.xml')
        
        #Load searcher object
        self.video = Video(self.config['sources'].as_list('video'))
        self.subtitle = Subtitle(self.config['sources'].as_list('subtitle'))
        self.information = Information(self.config['sources']['information'])
        
        #Load chooser object
        self.videochooser = VideoChooser('qualities.xml')
    
    def run(self):
        todownload = []
        for serie in self.db.get_series():
            todownload.extend( self.check(serie) )
        for ep in todownload:
            self.retrive(ep[0], ep[1], ep[2])
        
    def check(self, serie):
        todownload = []
        ep= self.information.get_episodes(serie['name'], serie['snum'])
        for ep in ep[serie['enum']:]:
            airdate = self.information.get_airdate(serie['name'], serie['snum'], ep)
            if airdate <= datetime.date.today():
                todownload.append( (serie['name'], serie['snum'], ep) )
        return todownload
    
    def retrive(self, name, snum, enum):
        logger.info('Process %s season %s episode %s' % (name, snum, enum) )
        vresults = self.video.tvshow_search(name, snum, enum, '720p')
        vid = self.videochooser.choose(vresults) # We need to choise
        print vid
        #~ logger.info('Video found: %s' % vid['torrent_name'])
        #~ subresults = self.subtitle.tvshow_search(name, snum, enum, 'fr')
        #~ sub = subresults[0] # We need to choise
        
if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    canape = Canape()
    canape.run()

