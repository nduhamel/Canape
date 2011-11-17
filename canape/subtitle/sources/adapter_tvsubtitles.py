#encoding:utf-8
#       adapter_tvsubtitles.py
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
import urllib
from tempfile import TemporaryFile
from zipfile import ZipFile
import logging

import tvsubtitles_api
from tvsubtitles_api.tvsubtitles_exceptions import tvsubtitles_languagenotfound

from canape.subtitle.tvshow import TvShowSubtitle
from canape.subtitle.subtitle import Subtitle
from canape.exceptions import UnexceptedContent

logger = logging.getLogger(__name__)

def getter(subtitleObj):
    f,h = urllib.urlretrieve(subtitleObj.download_url)
    zipf = ZipFile(f)
    zipfl = zipf.namelist()
    if not len(zipfl) == 1:
        raise UnexceptedContent()
    return zipf.open(zipfl[0])

class TvSubtitles(TvShowSubtitle):
    
    def __init__(self):
        self.tvsubtitles = tvsubtitles_api.TvSubtitles()
        
        #Mute tvsubtitles_api logger
        tvsubtitles_api_logger = logging.getLogger("tvsubtitles_api")
        tvsubtitles_api_logger.setLevel(logging.ERROR)
    
    def search(self, tvshow, snum, enum, language):
        try:
            subtitles = self.tvsubtitles[tvshow][snum][enum]['languages'][language]
            return [ self._translate(s) for s in subtitles]
        except tvsubtitles_languagenotfound as  strerror:
            logger.info(strerror)
            return []
    
    def _translate(self, subdict):
        return Subtitle(subdict['name'], subdict['download_url'],
                        keywords=[subdict['rip'], subdict['release']], 
                        sourcescore=self._score(subdict),
                        getter=getter)
    
    def _score(self, subdict):
        return int(subdict['good'])/(int(subdict['bad']) or 1)*int(subdict['downloaded'])
