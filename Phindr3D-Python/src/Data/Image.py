# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of src <https://github.com/DWALab/Phindr3D>.
#
# src is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# src is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with src.  If not, see <http://www.gnu.org/licenses/>.

from .Stack import Stack

class Image:
    """This class handles groups of image files and the associated metadata.
       Static methods that draw closely from transliterations of the MATLAB functions
       can be found in the DataFunctions class."""

    def __init__(self):
        """Image class constructor"""
        self.imageID = None
        self.stackLayers = {}
        pass

    def setImageID(self, number):
        self.imageID = number

    def addStackLayers(self, layerlist, columnlabels):
        # layerlist is a list of rows of metadata, each represented as a list of data elements
        for layer in layerlist:
            key = layer[layer.__len__() - 3] # index len - 3 will always be stack column
            self.setImageID(key)
            newStackLayer = Stack()
            newStackLayer.addChannels(layer, columnlabels)
            self.stackLayers[key] = newStackLayer





# end class Image



if __name__ == '__main__':
    """Tests of the Image class that can be run directly."""

    pass


# end main