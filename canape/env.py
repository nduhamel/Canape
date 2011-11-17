#encoding:utf-8
#       env.py
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
import os

class Environement(dict):
    """ A proxy object for user env 
    
    TODO: make it platform independent
    
    * Linux Desktop Standar directory:
    http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """
    def __init__(self):
        dict.__init__(self)
        self['HOME'] = os.environ['HOME']
        self['CONFIG_HOME'] = os.environ.get('XDG_CONFIG_HOME', self['HOME']+'/.config')
        self['DATA_HOME'] = os.environ.get('XDG_DATA_HOME', self['HOME']+'/.local/share')

class CanapeEnv(Environement):
    def __init__(self):
        Environement.__init__(self)
        self['CANAPE_CONFIG_FILE'] = self['CONFIG_HOME']+'/canape.ini'
        self['CANAPE_DATA_DIR'] = self['DATA_HOME']+'/canape'
        
