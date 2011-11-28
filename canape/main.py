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
        self.db = Canapedb(self.config['VIDEOS_DB'],
                           self.config['tvshow']['subtitles'],
                           self.config['tvshow']['quality'])

        #Load searcher object
        self.video = Video(self.config['sources']['video'])
        self.subtitle = Subtitle(self.config['sources']['subtitle'])
        self.information = Information()

        #Load chooser object
        self.videochooser = VideoChooser(self.config['QUALITIES_DB'])
        self.subtitlechooser = SubtitleChooser()

        #Load downloader object
        self.downloader = Downloader(config=self.config.get('downloader', {}))

    def daemon_run(self):
        """
        Launch periodically :meth:`Canape.check`.

        The launch interval is determined by the config file::

            [tvshow]
            check_interval = TIME IN MINUTES
        """
        if self.config['xmlrpc']['start']:
            server = CanapeXMLRPCServer(self.config['xmlrpc']['hostname'],
                                        self.config['xmlrpc']['port'])
            server.start()
        t = self.config['tvshow']['check_interval'] * 60
        while True:
            self.check()
            time.sleep(t)

    def check(self):
        """
        Process all series from database:

         1. First search for new episode with :meth:`Canape.updateEpisodes`
         2. Secondly search and download them with :meth:`Canape.getEpisodeDownload`
         3. Thirdly search and download subtitles with :meth:`Canape.getEpisodeSubtitles`
        """
        LOGGER.info("Start checking")

        self.downloader.check()

        for serie in self.db.get_series():
            LOGGER.info('Process serie: %s' % serie.name)
            serie = self.updateEpisodes(serie)
            updated_episodes = []
            for episode in serie.episodes:
                LOGGER.info('Process episode: S{0:0>2}E{1:0>2}'.format(episode.snum, episode.enum) )
                if episode.is_downloading():
                    isfinished=False
                    id_ =  "%sS%sE%s" % (serie.id_, episode.snum, episode.enum)
                    LOGGER.debug("Episode %s is downloading check that" % id_)
                    try:
                        isfinished = self.downloader.is_finished(id_)
                    except UnknownDownload:
                        LOGGER.error("Episode %s unknown from downloader guess it's downloaded" % id_ )
                        episode.set_downloaded()
                    if isfinished:
                        LOGGER.debug("Episode %s download finished" % id_)
                        episode.set_downloaded()

                elif not episode.is_downloaded():
                    LOGGER.info('Search for video')
                    video = self.getEpisodeDownload(serie, episode)
                    if video is not None:
                        video.id_ = "%sS%sE%s" % (serie.id_, episode.snum, episode.enum)
                        self.downloader.addVideo(video)
                        episode.set_downloading()

                if not episode.subtitle_downloaded():
                    LOGGER.info('Search for subtitles')
                    subtitle = self.getEpisodeSubtitles(serie, episode, video)
                    if subtitle is not None:
                        self.downloader.addSubtitle(subtitle)
                        episode.set_subtitle_downloaded()

                updated_episodes.append(episode)

            serie.episodes = updated_episodes
            self.db.update_serie(serie)

    def updateEpisodes(self, serieObj):
        """
        Update serieObj with new avalaible episodes return updated serieObj

        serieObj must be an instance of the :class:`canape.object.Serie` class.

        Get information by :py:class:`canape.information.Searcher` and test airdate.
        """
        serieObj.sort()
        lastest_ep = serieObj.episodes[-1]
        season_episodes= self.information.get_episodes(serieObj, lastest_ep.snum)
        time_delta = datetime.timedelta( hours=self.config['tvshow']['check_timedelta'] )
        for enum in season_episodes[lastest_ep.enum:]:
            airdate = self.information.get_airdate(serieObj, lastest_ep.snum, enum)
            if airdate + time_delta <= datetime.datetime.now():
                serieObj.episodes.append( Episode(lastest_ep.snum, enum) )
        return serieObj

    def getEpisodeDownload(self, serieObj, episodeObj):
        """
        Try to retrieve a download link for a specified serie's episode.
        Return an instance of the :class:`canape.video.video.Video` class or
        None.

        * serieObj must be an instance of the :class:`canape.object.Serie` class.
        * episodeObj must be an instance of the :class:`canape.object.Episode` class.

        Use :py:class:`canape.video.Searcher` for find video link and
        :py:class:`canape.chooser.VideoChooser` to choose the best.
        """
        vresults = self.video.tvshow_search(serieObj, episodeObj)
        if len(vresults):
            return self.videochooser.choose(vresults)
        else:
            return None

    def getEpisodeSubtitles(self, serieObj, episodeObj, videoObj=None):
        """
        Try to retrieve subtitles for a specified serie's episode.
        Return an instance of the :class:`canape.subtitle.subtitle.Subtitle` class or
        None.

        * serieObj must be an instance of the :py:class:`canape.object.Serie` class.
        * episodeObj must be an instance of the :py:class:`canape.object.Episode` class.
        * videoObj must be an instance of the :py:class:`canape.chooser.VideoChooser`

        Use :py:class:`canape.subtitle.Searcher` for find subtitle and
        :py:class:`canape.chooser.SubtitleChooser` to choose the best.
        """
        subtitles = self.subtitle.tvshow_search(serieObj, episodeObj)
        if len(subtitles):
            return self.subtitlechooser.choose(subtitles, videoObj)
        else:
            return None
