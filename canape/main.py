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
 python-daemon      http://pypi.python.org/pypi/python-daemon
"""
import logging
import datetime
import time

from canape.video import Searcher as Video
from canape.subtitle import Searcher as Subtitle
from canape.information import Searcher as Information
from canape.config import CanapeConfig
from canape.xmldb import Canapedb
from canape.chooser import VideoChooser, SubtitleChooser
from canape.downloader import Downloader
from canape.downloader.exceptions import UnknownDownload
from canape.object import Episode
from canape.xmlrpc import CanapeXMLRPCServer

LOGGER = logging.getLogger(__name__)

class Canape(object):

    def __init__(self):

        self.config = CanapeConfig()
        self.db = Canapedb(self.config['VIDEOS_DB'])

        #Load searcher object
        self.video = Video(self.config['sources'].as_list('video'))
        self.subtitle = Subtitle(self.config['sources'].as_list('subtitle'))
        self.information = Information()

        #Load chooser object
        self.videochooser = VideoChooser(self.config['QUALITIES_DB'])
        self.subtitlechooser = SubtitleChooser()

        #Load downloader object
        self.downloader = Downloader(config=self.config.get('downloader', {}))

    def daemon_run(self):
        server = CanapeXMLRPCServer()
        server.start()
        while True:
            self.check()
            t = self.config['tvshow'].as_int('check_interval')
            time.sleep(t*60)

    def check(self):
        LOGGER.info("Start checking")

        self.downloader.check()

        for serie in self.db.get_series():
            serie = self.updateEpisodes(serie)
            updated_episodes = []
            for episode in serie.episodes:

                if episode.is_downloading():
                    LOGGER.debug("Episode downloading check that...")
                    id_ =  "%sS%sE%s" % (serie.id_, episode.snum, episode.enum)
                    isfinished=False
                    try:
                        isfinished = self.downloader.is_finished(id_)
                    except UnknownDownload:
                        LOGGER.error("Episode %sS%sE%s unknown from downloader guess it's downloaded" % (serie.name, episode.snum, episode.enum))
                        episode.set_downloaded()
                    if isfinished:
                        LOGGER.debug("Episode downloaded!")
                        episode.set_downloaded()

                elif not episode.is_downloaded():
                    video = self.getEpisodeDownload(serie.name, episode, serie.quality)
                    if video is not None:
                        video.id_ = "%sS%sE%s" % (serie.id_, episode.snum, episode.enum)
                        self.downloader.addVideo(video)
                        episode.set_downloading()

                if not episode.subtitle_downloaded():
                    subtitle = self.getEpisodeSubtitles(serie, episode, video)
                    self.downloader.addSubtitle(subtitle)
                    episode.set_subtitle_downloaded()

                updated_episodes.append(episode)

            serie.episodes = updated_episodes
            self.db.update_serie(serie)

    def updateEpisodes(self, serieObj):
        """ First process step:
        take a serieObj and return an update serieObj with new episodes

        Get information by self.information and test airdate
        TODO need to check next season
        """
        lastest_ep = serieObj.episodes[-1]
        season_episodes= self.information.get_episodes(serieObj, lastest_ep.snum)
        for enum in season_episodes[lastest_ep.enum:]:
            airdate = self.information.get_airdate(serieObj, lastest_ep.snum, enum)
            if airdate <= datetime.date.today():
                serieObj.episodes.append( Episode(lastest_ep.snum, enum) )
        serieObj.sort()
        return serieObj

    def getEpisodeDownload(self, showname, episodeObj,quality=None):
        """ Second process step: try to retrive download link for an
        episode, return a Video object (canape.video.video.Video) or
        None """
        vresults = self.video.tvshow_search(showname, episodeObj.snum, episodeObj.enum, quality)
        if len(vresults):
            return self.videochooser.choose(vresults)
        else:
            return None

    def getEpisodeSubtitles(self, serieObj, episodeObj, videoObj=None):
        """ Third process step: try to retrive episode's subtitles
        return a subtitleObj or None"""
        if serieObj.subtitle is None:
            lang = self.config['tvshow']['subtitles']
        else:
            lang = serieObj.subtitle

        subtitles = self.subtitle.tvshow_search(serieObj.name, episodeObj.snum, episodeObj.enum, lang)
        return self.subtitlechooser.choose(subtitles, videoObj)
