#encoding:utf-8
#       video/video.py
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
from lxml import etree

class Video(object):

    def __init__(self, vtype, name, download_url,
                size=None, date=None, sourcescore=None, id_=None):
        """
        * type must be 'torrent' or 'directlink'
        * size must be an int in octet
        * date must be a datetime.datetime object
        * sourcescore must be a fload
        * id must be a string
        """
        self.vtype = vtype
        self.name = name
        self.download_url = download_url
        self.size = size
        self.date = date
        self.sourcescore = sourcescore or 1
        self.id_ = id_

    def __str__(self):
        return self.name

    def __repr__(self):
        extra = {}
        if self.size is not None:
            extra['size'] = str(self.size)
        if self.date is not None:
            extra['date'] = self.date.strftime("%Y-%m-%d %H:%M")
        if self.id_ is not None:
            extra['id_'] = self.id_

        video = etree.Element("video", name=self.name,
                             vtype=self.vtype,
                             download_url=self.download_url,
                             sourcescore=str(self.sourcescore),
                             **extra
                            )
        return etree.tostring(video,pretty_print=True)
