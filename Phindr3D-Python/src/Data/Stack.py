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
    from .ImageChannel import *
except ImportError:
    from ImageChannel import *

class Stack:
    """This class handles groups of image files and the associated metadata.
       Static methods that draw closely from transliterations of the MATLAB functions
       can be found in the DataFunctions class."""

    def __init__(self):
        """Stack class constructor"""
        self.channels = {}
        self.otherparams = {}

    def addChannels(self, row, columnlabels): # row is a list of elements from one row in metadata file
        # rowi (row index) used to iterate row alongside columns
        rowi = 0
        for col in columnlabels:
            if col.startswith('Channel_'):
                strlen = len(col)
                channelnum = int(col[8:strlen]) # channel number is always the 9th letter until end in 'Channel_X'
                newchan = ImageChannel()
                newchan.setPath(row[rowi])
                self.channels[channelnum] = newchan
            elif col.startswith('Stack'): # once iterator reaches 'Stack', no more additional params to store
                return
            else:
                self.otherparams[col] = row[rowi]
            rowi += 1
    # end addChannels

    def GetTreatment(self):
        """Treatment is an optional column in the metadata. If the column exists,
            this method returns the value from that column. If no Treatment value was
            found in the metadata, this method returns None."""
        try:
            return self.otherparams['Treatment']
        except KeyError:
            return None
    # end GetTreatment

    def GetNumChannels(self):
        """Get the number of channels in each stack layer"""
        return len(self.channels)
    # end GetNumChannels

# end class Stack

if __name__ == '__main__':
    """Tests of the Stack class that can be run directly."""

    pass


# end main