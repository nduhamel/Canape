#encoding:utf-8
#       xmldb.py
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
from threading import RLock
import logging

from lxml import etree

from canape.utils import synchronized
from canape.object import Serie, Episode

LOGGER = logging.getLogger(__name__)
LOCK = RLock()

class AlreadyExist(Exception):
    pass

class NotExist(Exception):
    pass

class Canapedb(object):

    def __init__(self, xmlfile):
        self.xmlfile = xmlfile

    @synchronized(LOCK)
    def add_serie(self, serieObj):

        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')

        try:
            for serie in self.get_series():
                if serie.name == serieObj.name:
                    raise AlreadyExist()
                tmp_file.write(repr(serie))
        except:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise
        else:
            tmp_file.write(repr(serieObj))
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)

    @synchronized(LOCK)
    def remove_serie(self, serie):

        if isinstance(serie, Serie):
            sname = serie.name

        tmp_found=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')

        for serie in self.get_series():
            if not serie.name == sname:
                tmp_file.write(repr(serie))
            else:
                tmp_found=True

        if tmp_found:
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise NotExist()

    @synchronized(LOCK)
    def update_serie(self, serieObj):

        tmp_found=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')

        for serie in self.get_series():
            if serie.name == serieObj.name:
                tmp_found=True
                tmp_file.write(repr(serieObj))
            else:
                tmp_file.write(repr(serie))

        if tmp_found:
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise NotExist()

    @synchronized(LOCK)
    def get_series(self):
        context = etree.iterparse(self.xmlfile, events=('end',), tag='serie')
        for event, elem in context:
            name = elem.attrib['name']
            quality = elem.attrib.get('quality', None)
            subtitle = elem.attrib.get('subtitle', None)
            id_ = elem.attrib.get('id_', None)
            ep=[]
            def return_ep(elem):
                snum = int(elem.attrib['snum'])
                enum = int(elem.attrib['enum'])
                state = int(elem.attrib['state'])
                ep.append(Episode(snum, enum, state))
            self._fast_iter_episode(elem,return_ep)
            #Clear memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            # Create a generator
            yield Serie(name, ep, quality=quality, subtitle=subtitle, id_=id_)
        del context

    def _fast_iter_episode(self, sele, function):
        context = etree.iterwalk(sele, events=('end',), tag='episode')
        for event, elem in context:
            function(elem)
            #Clear memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context
