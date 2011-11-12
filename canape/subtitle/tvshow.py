#encoding:utf-8
#       subtitle/tvshow.py
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

from canape.utils import PluginMount

class TvShowSubtitle:
    """ Base object for tvshow subtitle search web site API
    
    A TvShowSubtitle object must have a search(tvshow, snum, enum) 
    function that return a list of subtitle dicts with this key:
    * name (str)
    * uploaded_date (datetime)
    * download_url (str)
    And this optional keys:
    * downloaded_count (int)
    * score (int) between 0 and 10
    * rip (str)
    * release (str)

    """
    __metaclass__ = PluginMount
    
    def search(self, tvshow, snum, enum):
        raise NotImplementedError()