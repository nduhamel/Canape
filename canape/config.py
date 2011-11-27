#encoding:utf-8
#       config.py
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
from os.path import expanduser

from configobj import ConfigObj
from validate import Validator

import canape.env

class CanapeConfig(ConfigObj):
    def __init__(self):
        self.env = canape.env.CanapeEnv()
        ConfigObj.__init__(self,
                            infile=self.env['CANAPE_CONFIG_FILE'],
                            configspec=self.env['CANAPE_CONFIGSPEC_FILE'],
                            interpolation=False
                            )
        validator = Validator()
        self.validate(validator)
        self['VIDEOS_DB'] = self.env['CANAPE_DATA_DIR']+'/videos.xml'
        self['QUALITIES_DB'] = self.env['CANAPE_DATA_DIR']+'/qualities.xml'
        self['DOWNLOADS_DB'] = self.env['CANAPE_DATA_DIR']+'/downloads.xml'

        self['downloader']['DOWNLOADS_DB'] = self['DOWNLOADS_DB']
        #download_dir
        #Expenduser
        self['downloader']['download_dir'] = expanduser(self['downloader']['download_dir'])
        #Add download_dir to all downloader adapter config
        for adpatername in self['downloader']['adapters']:
            self['downloader']['adapters'][adpatername]['download_dir'] = self['downloader']['download_dir']
