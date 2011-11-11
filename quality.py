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

# http://filesharingtalk.com/threads/311830-The-Official-Scene-Dictionary

# 720p 1g a 2.5g

DEFAULT_QUALITY = [
        {'name': '1080p', 'size': (5000, 20000), 'label': '1080P', 'alternative': [], 'ext':['mkv', 'm2ts']},
        {'name': '720p', 'size': (3500, 10000), 'label': '720P', 'alternative': [], 'ext':['mkv', 'm2ts']},
        #~ {'name': ''
        #~ {'name': 'brrip', 'size': (700, 7000), 'label': 'BR-Rip', 'alternative': ['bdrip'], 'ext':['mkv', 'avi']},
        #~ {'name': 'dvdr', 'size': (3000, 10000), 'label': 'DVD-R', 'alternative': [], 'ext':['iso', 'img']},
        #~ {'name': 'dvdrip', 'size': (600, 2400), 'label': 'DVD-Rip', 'alternative': [], 'ext':['avi', 'mpg', 'mpeg']},
        #~ {'name': 'scr', 'size': (600, 1600), 'label': 'Screener', 'alternative': ['dvdscr', 'ppvrip'], 'ext':['avi', 'mpg', 'mpeg']},
        #~ {'name': 'r5', 'size': (600, 1000), 'label': 'R5', 'alternative': [], 'ext':['avi', 'mpg', 'mpeg']},
        #~ {'name': 'tc', 'size': (600, 1000), 'label': 'TeleCine', 'alternative': ['telecine'], 'ext':['avi', 'mpg', 'mpeg']},
        #~ {'name': 'ts', 'size': (600, 1000), 'label': 'TeleSync', 'alternative': ['telesync'], 'ext':['avi', 'mpg', 'mpeg']},
        #~ {'name': 'cam', 'size': (600, 1000), 'label': 'Cam', 'alternative': [], 'ext':['avi', 'mpg', 'mpeg']}
        ]

class Quality:
    """ Represent a video quality """
    
    def __init__(self, label, name, size, ext, alternative=[]):
        """
        Keyword arguments:
        label -- str label for user display
        name  -- str name searched in file name
        size  -- tuple of int (min,max) in megaoctet
        ext   -- tuple of str contain all accepted file extension
        alternative -- tuple of string accepted if name isn't found
        """
        self.label = label
        self.name = name
        self.size = size
        self.ext = ext
        self.alternative = alternative
        
    def score(self, filename, size=None, ext=None):
        """ return a concordance score between the filename
        and the quality
        return int [0;100]
        """
        score = 0
        # if name, size and ext concord we can believe it's ok
        if self.name in filename:
            score += 40
        else: 
            score -= 40
            
        if size:
            if size >= self.size[0] and size <= self.size[1]:
                score += 30
            elif size < self.size[0]:
                score -= 30
            elif size > self.size[1]:
                score += 20
        
        if ext:
            if ext in self.ext:
                score += 30
            else:
                score -= 50 #Realy bad !!
        
        if score < 0:
            score = 0
        return score

class Qualities:
    """ Container and interface for all kowned qualities """
    
    def __init__(self):
        self._qualities = []
        #Load default:
        for q in DEFAULT_QUALITY:
           self._qualities.append( Quality(q['label'],q['name'], 
                                           q['size'], q['ext'], 
                                           q['alternative']
                                           )
           )
    
    def __str__(self):
        return "/".join([q.label for q in self._qualities])
    
    def get_quality(self, filename, size=None, ext=None):
        """ return the quality most likely """
        result = []
        for q in self._qualities:
            result.append( (q.label , q.score(filename, size, ext)))
        result = sorted(result, key=lambda q: q[1], reverse=True)
        if result[0][1]:
            return result[0]
        else:
            return None

if __name__ == '__main__':
    print "Knowed qualities: "+str(Qualities())
    
