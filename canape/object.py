#encoding:utf-8
#       object.py
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
from operator import attrgetter

from lxml import etree

class Serie(object):
    """
    :class:`Serie` represent a serie in Canape

    An intance of :class:`Serie` class have this attributes:
     * :attr:`name` the serie name
     * :attr:`id_` the serie's TVRage id
     * :attr:`datestr` on air date string (exemple: 2004-2011)
     * :attr:`episodes` a list of episodes, all item are instances of :class:`Episode` class
     * :attr:`subtitle` two letter contry code of the subtitle language or **None**
     * :attr:`quality` quality label or **None**
    """

    def __init__(self, name=None, episodes=None, quality=None,
                 subtitle=None, id_=None, datesstr=None):
        """
        :class:`Serie`'s constructor, it can be populate from a json or
        xml representation of an instance.
        """
        self.name = name

        #Allow populate object from json response
        if isinstance(episodes, list):
            new_episodes = [Episode(**kwargs) for kwargs in episodes if isinstance(kwargs, dict)] #Dict to Episode
            new_episodes.extend([ep for ep in episodes if isinstance(ep, Episode) ]) #Keep Episode
            episodes = new_episodes

        self.episodes = episodes or []
        self.quality = quality
        self.subtitle = subtitle
        self.id_ = id_
        self.datesstr = datesstr

    def sort(self):
        self.episodes = sorted(self.episodes, key=attrgetter('snum','enum'))

    def __repr__(self):
        """ Return an xml representation of the :class:`Serie` instance """
        extra = {}
        if self.quality is not None:
            extra['quality'] = self.quality
        if self.subtitle is not None:
            extra['subtitle'] = self.subtitle
        if self.id_ is not None:
            extra['id_'] = self.id_
        serie = etree.Element("serie", name=self.name, datesstr=self.datesstr, **extra)
        for ep in self.episodes:
            serie.append(ep.get_element())
        return etree.tostring(serie,pretty_print=True)

class Episode(object):
    """
    :class:`Episode` represent an episode in Canape

    An intance of :class:`Episode` class have this attributes:
     * :attr:`snum` the episode season number
     * :attr:`enum` the episode number
     * :attr:`state` internal state of the episode it can be intersection of this values:

         * :attr:`Episode.WAITING`
         * :attr:`Episode.SUBTITLE_DOWNLOADED`
         * :attr:`Episode.VIDEO_DOWNLOADING`
         * :attr:`Episode.VIDEO_DOWNLOADED`

    Don't modify it manualy use the object methods
    """

    WAITING = 1
    SUBTITLE_DOWNLOADED = 2
    VIDEO_DOWNLOADING = 4
    VIDEO_DOWNLOADED = 8

    def __init__(self, snum=None, enum=None, state=None):
        self.snum = int(snum)
        self.enum = int(enum)
        if state is None:
            self.state = self.WAITING
        else:
            self.state = int(state)

    def set_downloading(self):
        """ Set the :class:`Episode` instance video as downloading """
        self.state = self.state | self.VIDEO_DOWNLOADING

    def set_downloaded(self):
        """ Set the :class:`Episode` instance video as downloaded """
        self.state = self.state | self.VIDEO_DOWNLOADED

    def is_downloading(self):
        """ Return True if the :class:`Episode` instance video is downloading """
        return self.state & self.VIDEO_DOWNLOADING and not self.state & self.VIDEO_DOWNLOADED

    def is_downloaded(self):
        """ Return True if the :class:`Episode` instance video is downloaded """
        return self.state & self.VIDEO_DOWNLOADING and  self.state & self.VIDEO_DOWNLOADED

    def set_subtitle_downloaded(self):
        """ Set the :class:`Episode` instance subtitle as downloaded """
        self.state = self.state | self.SUBTITLE_DOWNLOADED

    def subtitle_downloaded(self):
        """ Return True if the :class:`Episode` instance subtitle is downloaded """
        return self.state & self.SUBTITLE_DOWNLOADED

    def get_element(self):
        """ Return the xml representation of the :class:`Episode` instance """
        return etree.Element("episode", snum=str(self.snum), enum=str(self.enum),state=str(self.state))
