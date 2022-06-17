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

try:
    from .Stack import Stack
except ImportError:
    from Stack import Stack

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
    # end addStackLayers

    def GetTreatment(self):
        """Treatment is an optional column in the metadata. Treatment values are stored
            on separate lines, though one image should have a unique treatment value.
            This method gets the Treatment values from the member stackLayers, if they exist.
            If they are all None, this method returns None. If there is a unique non-None value,
            this method returns that value. If there are multiple values, this method returns a list
            of the different values found."""
        tmpList = []
        try:
            for stkID in self.stackLayers:
                tmpList.append(self.stackLayers[stkID].GetTreatment())
        except AttributeError:
            return None
        # Use set to find unique values in a list, then change type back to list
        treatmentValList = list(set(tmpList))
        if len(treatmentValList) == 0:
            return None
        elif len(treatmentValList) == 1:
            return treatmentValList[0]
        else:
            return treatmentValList
    # end GetTreatment

# end class Image



if __name__ == '__main__':
    """Tests of the Image class that can be run directly."""

    pass


# end main