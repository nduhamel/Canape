#encoding:utf-8
#       subtitle/subtitle.py
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

class Subtitle(object):
    
    def __init__(self, name, download_url=None,
                keywords=None, sourcescore=None, getter=None):
        """
        * keywords must be a list of string
        * sourcescore must be a numeric type
        * getter must be a callable, that return the subtitle file object
        """
        if download_url is None and not callable(getter):
            raise AttributeError()
        
        self.name = name
        self.download_url = download_url
        self.getter = getter
        self.keywords = keywords or []
        self.sourcescore = sourcescore or 1
    
    def __str__(self):
        return self.name
    
    def getFile(self):
        """ Return the subtitle file object """
        if self.getter is not None:
            return self.getter(self)
        else:
            return urllib.urlopen(self.download_url)
