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

logger = logging.getLogger(__name__)
LOCK = Lock()

class Canapedb(object):
    
    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
    
    @synchronized(LOCK)
    def add_serie(self, name, lastest_snum, lastest_enum):
        """ Current approach:
        1/ Iter all db and copy it to a tempfile
        2/ Add node
        3/ move tempfile to xmlfile and erase the old one
        
        Pros:
         - Don't put the all xml file in memory
        Cons:
         - Many file access
        """
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')
        def do(elem):
            tmp_file.write( etree.tostring(elem,pretty_print=False))
        # Copy original
        self._fast_iter(do)
        # Add serie:
        serie = etree.Element("serie", name=name)
        etree.SubElement(serie, "episode", snum=str(lastest_snum), enum=str(lastest_enum))
        tmp_file.write(etree.tostring(serie,pretty_print=True))
        logger.debug('Add %s to season %s episode %s' % (name, lastest_snum, lastest_enum))
        #End
        tmp_file.write('</series>')
        tmp_file.close()
        shutil.move(tmp_file.name, self.xmlfile)
        
    @synchronized(LOCK)
    def update_serie(self, name, new_snum, new_enum):
        self.tmpfound=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<series>\n')
        def do(elem):
            if elem.attrib['name'] == name:
                self.tmpfound=True
                logger.debug('Update %s to season %s episode %s' % (name, new_snum, new_enum))
                serie = etree.Element("serie", name=name)
                etree.SubElement(serie, "episode", snum=str(new_snum), enum=str(new_enum))
                tmp_file.write( etree.tostring(serie,pretty_print=False))
            else:
                tmp_file.write( etree.tostring(elem,pretty_print=False))
        # Copy original
        self._fast_iter(do)
        if self.tmpfound:
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            logger.error("Can't update %s because it don't exist in db" % name)
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
                logger.debug('Remove %s' % name)
        # Copy original
        self._fast_iter(do)
        if self.tmpfound:
            tmp_file.write('</series>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            logger.error("Can't remove %s because it don't exist in db" % name)
            tmp_file.close()
            os.remove(tmp_file.name)
    
    @synchronized(LOCK)
    def get_series(self):
        context = etree.iterparse(self.xmlfile, events=('end',), tag='serie')
        for event, elem in context:
            name = elem.attrib['name']
            snum = int(elem[0].attrib['snum'])
            enum = int(elem[0].attrib['enum'])
            #Clear memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            # Create a generator
            yield {'name':name, 'snum':snum, 'enum':enum}
        del context
    
    def _fast_iter(self, function):
        context = etree.iterparse(self.xmlfile, events=('end',), tag='serie')
        for event, elem in context:
            function(elem)
            #Clear memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context

if __name__ == '__main__':
    db = Canapedb('testdb.xml')
    print "All series:"
    for s in db.get_series():
        print s
    print '-----------------------------------------'
    print 'Add Dr House and print:'
    db.add_serie('Dr House', 1,1)
    for s in db.get_series():
        print s
    print '------------------------------------------'
    print 'Update Dr House to season 3, episode 4 and print'
    db.update_serie('Dr House', 3, 4)
    for s in db.get_series():
        print s
    print '------------------------------------------'
    print 'Remove Dr House and print:'
    db.remove_serie('Dr House')
    for s in db.get_series():
        print s
