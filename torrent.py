#encoding:utf-8
#       torrent.py
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

class TorrentSearcher:
    """ Base object for torrent search web site API
    
    A TorrentSearcher object must have a search() function that return a
    list of torrent dict with this key:
    * torrent_name (str)
    * torrent_size (octet int)
    * uploaded_date (datetime)
    * torrent_url (str)
    * seeders (int)
    * leechers (int)
    and an optional torrent_score key (int between 0 and 10) calculated
    with the web site specific data (eg: user type, note)
    """

    def search(self, term, quality=None):
        raise NotImplementedError()
