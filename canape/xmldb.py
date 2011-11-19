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
from threading import Lock
import logging

from lxml import etree

from canape.utils import synchronized

LOGGER = logging.getLogger(__name__)
LOCK = Lock()

WAITING = 1
SUBTITLE_DOWNLOADED = 2
VIDEO_DOWNLOADING = 4
VIDEO_DOWNLOADED = 8

class Canapedb(object):
    
    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
    
    @synchronized(LOCK)
    def add_serie(self, name, lastest_snum, lastest_enum, state=None, quality=None, subtitle=None):
        """ Current approach:
        1/ Iter all db and copy it to a tempfile
        2/ Add node
        3/ move tempfile to xmlfile and erase the old one
        
        Pros:
         - Don't put the all xml file in memory
        Cons:
         - Many file access
        """
        state = state or WAITING
        extra = {}
        if quality is not None:
            extra['quality'] = quality
        if subtitle is not None:
            extra['subtitle'] = subtitle
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')
        def do(elem):
            tmp_file.write( etree.tostring(elem,pretty_print=False))
        # Copy original
        self._fast_iter_serie(do)
        # Add serie:
        serie = etree.Element("serie", name=name, **extra)
        etree.SubElement(serie, "episode", snum=str(lastest_snum), enum=str(lastest_enum), state=str(state))
        tmp_file.write(etree.tostring(serie,pretty_print=True))
        LOGGER.debug('Add %s to season %s episode %s' % (name, lastest_snum, lastest_enum))
        #End
        tmp_file.write('</series>')
        tmp_file.close()
        shutil.move(tmp_file.name, self.xmlfile)
        
    @synchronized(LOCK)    
    def add_episode(self, sname, snum, enum, state=None):
        state = state or WAITING
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')
        def do(elem):
            if elem.attrib['name'] == sname:
                etree.SubElement(elem, "episode", snum=str(snum), enum=str(enum),state=str(state))
            tmp_file.write( etree.tostring(elem,pretty_print=False))
        # Copy original
        self._fast_iter_serie(do)
        if self.tmpfound:
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            LOGGER.error("Can't update %s because it don't exist in db" % name)
            tmp_file.close()
            os.remove(tmp_file.name)
            
    @synchronized(LOCK)    
    def remove_episode(self, sname, snum, enum):
        self.tmpfound=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')
        def do(elem):
            if elem.attrib['name'] == sname:
                serie = etree.Element("serie", name=sname)
                def return_ep(elem):
                    ep_snum = int(elem.attrib['snum'])
                    ep_enum = int(elem.attrib['enum'])
                    ep_state = int(elem.attrib['state'])
                    if not ep_snum == snum or not ep_enum == enum :
                        etree.SubElement(serie, "episode", snum=str(ep_snum), enum=str(ep_enum),state=str(ep_state))
                    else:
                        self.tmpfound=True
                self._fast_iter_episode(elem,return_ep)
                tmp_file.write( etree.tostring(serie,pretty_print=False))
            else:
                tmp_file.write( etree.tostring(elem,pretty_print=False))
        # Copy original
        self._fast_iter_serie(do)
        if self.tmpfound:
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            LOGGER.error("Can't delete because it don't exist in db" )
            tmp_file.close()
            os.remove(tmp_file.name)
        
        
    @synchronized(LOCK)
    def update_episode(self, name, snum, enum, state):
        """ Update serie's episode state """
        if state == WAITING:
            return
        self.tmpfound=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')
        def do(elem):
            if elem.attrib['name'] == name:
                serie = etree.Element("serie", name=name)
                def return_ep(elem):
                    ep_snum = int(elem.attrib['snum'])
                    ep_enum = int(elem.attrib['enum'])
                    ep_state = int(elem.attrib['state'])
                    if ep_snum == snum and ep_enum == enum:
                        ep_state = ep_state | state
                        self.tmpfound=True
                    etree.SubElement(serie, "episode", snum=str(snum), enum=str(enum),state=str(ep_state))
                self._fast_iter_episode(elem,return_ep)
                tmp_file.write( etree.tostring(serie,pretty_print=False))
            else:
                tmp_file.write( etree.tostring(elem,pretty_print=False))
        # Copy original
        self._fast_iter_serie(do)
        if self.tmpfound:
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            LOGGER.error("Can't update %s because it don't exist in db" % name)
            tmp_file.close()
            os.remove(tmp_file.name)
    
    @synchronized(LOCK)
    def remove_serie(self, name):
        """ Current approach:
        1/ Iter all db and copy it to a tempfile
           only if serie's name is not name
        3/ move tempfile to xmlfile and erase the old one
        
        Pros:
         - Don't put the all xml file in memory
        Cons:
         - Many file access
        """
        self.tmpfound=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')
        def do(elem):
            if not elem.attrib['name'] == name:
                tmp_file.write( etree.tostring(elem,pretty_print=False))
            else:
                self.tmpfound = True
                LOGGER.debug('Remove %s' % name)
        # Copy original
        self._fast_iter_serie(do)
        if self.tmpfound:
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            LOGGER.error("Can't remove %s because it don't exist in db" % name)
            tmp_file.close()
            os.remove(tmp_file.name)
    
    @synchronized(LOCK)
    def get_series(self):
        context = etree.iterparse(self.xmlfile, events=('end',), tag='serie')
        for event, elem in context:
            name = elem.attrib['name']
            quality = elem.attrib.get('quality', None)
            subtitle = elem.attrib.get('subtitle', None)
            ep=[]
            def return_ep(elem):
                snum = int(elem.attrib['snum'])
                enum = int(elem.attrib['enum'])
                state = int(elem.attrib['state'])
                ep.append({'snum':snum,'enum':enum,'state':state})
            self._fast_iter_episode(elem,return_ep)
            #Clear memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            # Create a generator
            yield {'name':name, 'episodes':ep, 'quality':quality, 'subtitle':subtitle}
        del context
    
    def _fast_iter_serie(self, function):
        context = etree.iterparse(self.xmlfile, events=('end',), tag='serie')
        for event, elem in context:
            function(elem)
            #Clear memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
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

if __name__ == '__main__':
    db = Canapedb('textdb.xml')
    print "All series:"
    for s in db.get_series():
        print s
    print '-----------------------------------------'
    print 'Add Dr House 720p and print:'
    db.add_serie('Dr House', 1,1,quality='720p')
    for s in db.get_series():
        print s
    print '------------------------------------------'
    print 'Update Dr House to season 1, episode 1 to VIDEO_DOWNLOADING and print'
    db.update_episode('Dr House', 1, 1, state=VIDEO_DOWNLOADING)
    for s in db.get_series():
        print s
    print '------------------------------------------'
    print 'Update Dr House to season 1, episode 1 to SUBTITLE_DOWNLOADED and print'
    db.update_episode('Dr House', 1, 1, state=SUBTITLE_DOWNLOADED)
    for s in db.get_series():
        print s
    print '------------------------------------------'
    print 'Add Dr House season 1, episode 2 and print'
    db.add_episode('Dr House', 1, 2)
    for s in db.get_series():
        print s
    print '------------------------------------------'
    print 'Remove Dr House season 1, episode 1 and print'
    db.remove_episode('Dr House', 1, 1)
    for s in db.get_series():
        print s
    print '------------------------------------------'
    print 'Remove Dr House and print:'
    db.remove_serie('Dr House')
    for s in db.get_series():
        print s
