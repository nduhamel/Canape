#encoding:utf-8
#       chooser.py
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
import logging

from canape.quality import Qualities
from canape.utils.string import dice_coefficient

LOGGER = logging.getLogger(__name__)

class VideoChooser(object):

    def __init__(self, qualitiesdb):
        self.qualities = Qualities(qualitiesdb)

    def choose(self, video_list, quality=None):

        if quality is None:
            return video_list[0]
        else:
            #Ordered list of qualities
            quality_result = [self.qualities.quality_bet(vid.name, vid.size,) for vid in video_list]
            #Mix them  [ ( ('quality',score), vid), ...]
            vidq = zip(quality_result, video_list)
            #Delete uneded quality
            vidq = [vid for vid in vidq if vid[0][0] == quality]
            #Get max quality score
            max_quality_score = max(vidq,key=lambda mixed: mixed[0][1])[0][1]
            #Return first vid with max score:
            for q, vid in vidq:
                if q[1] == max_quality_score:
                    return vid

class SubtitleChooser(object):

    def choose(self, sublist, videoObj=None):

        if videoObj is None:
            return sublist[0]

        scored=[ (dice_coefficient(s.name, videoObj.name), s) for s in sublist]
        return sorted(scored, key=lambda t: t[0], reverse=True)[0][1]
