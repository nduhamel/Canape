#encoding:utf-8
#       xmlrpc.py
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
from SimpleXMLRPCServer import SimpleXMLRPCServer
import threading

from canape.config import CanapeConfig
from canape.xmldb import Canapedb
from canape.object import Serie


class CanapeInterface(object):

    def __init__(self):
        self.config = CanapeConfig()
        self.db = Canapedb(self.config['VIDEOS_DB'])

    def get_series(self):
        return list(self.db.get_series())

    def add_serie(self, seriejson):
        serie = Serie(**seriejson)
        self.db.add_serie(serie)
        return 1


class CanapeXMLRPCServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.server = SimpleXMLRPCServer(("localhost", 8080))

    def run(self):
        self.server.register_instance(CanapeInterface())
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()