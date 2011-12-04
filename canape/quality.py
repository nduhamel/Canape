#encoding:utf-8
#       quality.py
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

from canape.utils.thread import synchronized

LOGGER = logging.getLogger(__name__)
LOCK = Lock()

class Quality(object):

    def __init__(self,
                 label=None,
                 size=None,
                 extensions=[],
                 keywords=[],
                 extras=[],
                 fromxml=None):

        if fromxml is not None:
            self._from_xml(fromxml)
        else:
            if label == None or size == None:
                raise ValueError()

            self.label = label
            self.size = size
            self.extensions = extensions
            self.keywords = keywords
            self.extras = extras

    def _from_xml(self, xml):
        for e in xml:
            if e.tag == 'label':
                setattr(self, 'label', e.text.lower())
            elif e.tag == 'size':
                setattr(self, 'size', (float(e.attrib['min']), float(e.attrib['max'])))
            else:
                setattr(self, e.tag, [child.text.lower() for child in e.iterchildren()])

    def _to_xml(self):
        ele_quality = etree.Element("quality")
        etree.SubElement(ele_quality, "label").text = self.label
        etree.SubElement(ele_quality, "size", min=str(self.size[0]), max=str(self.size[1]))
        ele_extensions = etree.Element("extensions")
        for ext in self.extensions:
            etree.SubElement(ele_extensions, "ext").text = ext
        ele_quality.append(ele_extensions)

        ele_keywords = etree.Element("keywords")
        for keyword in self.keywords:
            etree.SubElement(ele_keywords, "keyword").text = keyword
        ele_quality.append(ele_keywords)

        ele_extras = etree.Element("extras")
        for extra in self.extras:
            etree.SubElement(ele_extras, "extra").text = extra
        ele_quality.append(ele_extras)
        return etree.tostring(ele_quality,pretty_print=True)

    def test_quality(self, name, size=None, extension=None):
        scoring = {'label': 50, 'extensions': 30, 'size': 25, 'keywords': 10, 'extras': 5 }
        name = name.lower()
        score = 0

        if self.label in name:
            score += scoring['label']
        else:
            score -= scoring['label']

        if size is not None:
            if size >= self.size[0] and size <= self.size[1]:
                score += scoring['size']
            else:
                score -= scoring['size']

        if extension is not None:
            found = False
            for ext in self.extensions:
                if ext == extension:
                    score += scoring['extensions']
                    found = True
            if found == False:
                score -= scoring['extensions']

        for keyword in self.keywords:
            if keyword in name:
                score += scoring['keywords']

        for extra in self.extras:
            if keyword in name:
                score += scoring['extras']
        return score

    def __repr__(self):
        return self._to_xml()

    def __str__(self):
        return self.label

class Qualities(object):
    def __init__(self, qualitiesdb):
        self.db = Qualitiesdb(qualitiesdb)
        self.qualities = list(self.db.iter_qualities())

    def compute_scoring(self, name, size=None, extension=None):
        """ Compute qualities score
        return a dict with:
            * quality's label as key
            * score as value """
        r = {}
        for q in self.qualities:
            r[q.label] = q.test_quality(name, size, extension)
        return r

    def quality_bet(self, name, size=None, extension=None):
        """ Try to determine the quality
        return a tuple (quality, score)
        * quality is the quality label
        * score is an int
         """
        computed = self.compute_scoring(name, size, extension)
        return max(computed.items(), key=lambda q: q[1])

class Qualitiesdb(object):

    def __init__(self, xmlfile):
        self.xmlfile = xmlfile

    @synchronized(LOCK)
    def add_quality(self, quality):
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<qualities>\n')
        def do(elem):
            tmp_file.write( etree.tostring(elem,pretty_print=False))
        # Copy original
        self._fast_iter(do)
        # Add quality:
        tmp_file.write(repr(quality))
        #End
        tmp_file.write('</qualities>')
        tmp_file.close()
        shutil.move(tmp_file.name, self.xmlfile)

    @synchronized(LOCK)
    def remove_quality(self, label):
        self.tmpfound=False
        tmp_file  = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write('<qualities>\n')
        def do(elem):
            if self.tmpfound:
                tmp_file.write( etree.tostring(elem,pretty_print=False))
                return
            for child in elem.iterchildren():
                if child.tag == 'label' and child.text == label:
                    self.tmpfound = True
                    LOGGER.debug('Remove %s' % label)
                    break
            if not self.tmpfound:
                tmp_file.write( etree.tostring(elem,pretty_print=False))
        # Copy original
        self._fast_iter(do)
        if self.tmpfound:
            tmp_file.write('</qualities>')
            tmp_file.close()
            shutil.move(tmp_file.name, self.xmlfile)
        else:
            LOGGER.error("Can't remove %s because it don't exist in db" % name)
            tmp_file.close()
            os.remove(tmp_file.name)

    @synchronized(LOCK)
    def iter_qualities(self):
        context = etree.iterparse(self.xmlfile, events=('end',), tag='quality')
        for event, elem in context:
            # Create a generator
            yield Quality(fromxml=elem)
            #Clear memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context

    def _fast_iter(self, function):
        context = etree.iterparse(self.xmlfile, events=('end',), tag='quality')
        for event, elem in context:
            function(elem)
            #Clear memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context

