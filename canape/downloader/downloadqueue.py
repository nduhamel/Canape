#encoding:utf-8
#       downloader/downloadqueue.py
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
import tempfile
import shutil
import os
import datetime
from threading import RLock
import logging

from lxml import etree

from canape.video.video import Video
from canape.utils import synchronized

LOGGER = logging.getLogger(__name__)
LOCK = RLock()

class AlreadyExist(Exception):
    pass

class DownloadQueue(object):

    WAITING = 0
    STARTED = 1

    def __init__(self, xmlfile):
        self.xmlfile = xmlfile

    @synchronized(LOCK)
    def append(self, videoObject, state=None):

        state = state or self.WAITING

        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<downloads>\n')

        try:
            for download in self:
                if download.name == videoObject.name:
                    raise AlreadyExist()
                tmp_file.write(repr(download))
        except:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise
        else:
            videoObject.extra['state'] = str(state)
            tmp_file.write(repr(videoObject))
            tmp_file.write('</downloads>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)

    @synchronized(LOCK)
    def pop(self, filterby=None):

        filterby = filterby or self.WAITING

        tmp_found=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<downloads>\n')

        first = False

        for download in self:
            if not first and download.extra['state'] == filterby:
                first = download
            else:
                tmp_file.write(repr(download))

        if first:
            tmp_file.write('</downloads>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
            return first
        else:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise IndexError()

    @synchronized(LOCK)
    def remove(self, videoid):

        tmp_found=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<downloads>\n')

        for download in self:
            if not download.id_ == videoid:
                tmp_file.write(repr(download))

        tmp_file.write('</downloads>')
        tmp_file.close()
        shutil.move(tmp_file.name, self.xmlfile)

    @synchronized(LOCK)
    def __iter__(self):
        context = etree.iterparse(self.xmlfile, events=('end',), tag='video')
        for event, elem in context:
            name = elem.attrib.pop('name')
            vtype = elem.attrib.pop('vtype')
            download_url = elem.attrib.pop('download_url')
            size = elem.attrib.pop('size', None)
            date = elem.attrib.pop('date', None)
            id_ = elem.attrib.pop('id_', None)
            state = int(elem.attrib.pop('state'))
            if size is not None:
                size = int(size)
            if date is not None:
                date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M")
            sourcescore = float(elem.attrib.pop('sourcescore'))
            # Create a generator
            yield Video(vtype, name, download_url,
                        size=size, date=date, sourcescore=sourcescore, id_=id_, state=state, **elem.attrib)
        del context

