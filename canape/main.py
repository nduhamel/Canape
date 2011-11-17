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
 transmissionrpc    http://packages.python.org/transmissionrpc/
 bencode            http://pypi.python.org/pypi/bencode/  for .torrent decode
"""
import logging
import datetime

from canape.video import Searcher as Video
from canape.subtitle import Searcher as Subtitle
from canape.information import Searcher as Information
from canape.config import CanapeConfig
from canape.xmldb import Canapedb
from canape.chooser import VideoChooser, SubtitleChooser
from canape.downloader.downloader import Downloader

LOGGER = logging.getLogger(__name__)

class Canape(object):
    
    def __init__(self):
        
        self.config = CanapeConfig()
        self.db = Canapedb(self.config['VIDEOS_DB'])
        
        #Load searcher object
        self.video = Video(self.config['sources'].as_list('video'))
        self.subtitle = Subtitle(self.config['sources'].as_list('subtitle'))
        self.information = Information(self.config['sources']['information'])
        
        #Load chooser object
        self.videochooser = VideoChooser(self.config['QUALITIES_DB'])
        self.subtitlechooser = SubtitleChooser()
        
        #Load downloader object
        self.downloader = Downloader(config=self.config.get('downloader', {}))
    
    def run(self):
        todownload = []
        #First step
        for lastep in self.db.get_series():
            todownload.extend( self.getEpisodeToProcess(lastep['name'], 
                                lastep['snum'], lastep['enum']) 
                            )
        
        for ep in todownload:
            quality = self.config['tvshow']['default_quality']
            video = self.getEpisodeDownload(ep[0], ep[1], ep[2], quality)
            #~ self.downloader.addVideo(video)
            lang = self.config['tvshow']['subtitles']
            subtitle = self.getEpisodeSubtitles(ep[0], ep[1], ep[2], lang, video)
            self.downloader.addSubtitle(subtitle)
        
    
    def getEpisodeToProcess(self, showname, lastep_snum, lastep_enum):
        """ First process step:
        return a list of episode tuple (showname, snum, enum) to download
        
        Get information by self.information and test airdate
        """
        todownload = []
        ep= self.information.get_episodes(showname, lastep_snum)
        for ep in ep[lastep_enum:]:
            airdate = self.information.get_airdate(showname, lastep_snum, ep)
            if airdate <= datetime.date.today():
                todownload.append( (showname, lastep_snum, ep) )
        LOGGER.info('For serie: "%s" episodes to download: %s' % (showname, todownload))
        return todownload
    
    def getEpisodeDownload(self, showname, snum, enum, quality=None):
        """ Second process step: try to retrive download link for an 
        episode, return a Video object (canape.video.video.Video) or 
        None """
        vresults = self.video.tvshow_search(showname, snum, enum, quality)
        return self.videochooser.choose(vresults) or None
    
    def getEpisodeSubtitles(self, showname, snum, enum, language, videoObj=None):
        """ Third process step: try to retrive episode's subtitles 
        return a subtitleObj or None"""
        subtitles = self.subtitle.tvshow_search(showname, snum, enum, language)
        return self.subtitlechooser.choose(subtitles, videoObj)


        
if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    canape = Canape()
    canape.run()

