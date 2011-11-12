#encoding:utf-8
#       information/tvshow.py
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

class TvShow:
    """ Base object for tvshow informations sources 
    
    TvShow object api description:
    All information are retrieved by dictionary interface 
    (eg: __getitem__() )
    
    exemple:
       >> tvshow['dexter'][1][2]
    return the dexter second episode of season one
       >> tvshow['dexter']
    return seasons list
       >> tvshow['dexter'][1] 
    return episodes list
    
    """
    
    __metaclass__ = PluginMount
