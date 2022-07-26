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
    from .VoxelFunctions import *
except ImportError:
    from VoxelFunctions import *

try:
    from ..PhindConfig.PhindConfig import *
except ImportError:
    from src.PhindConfig.PhindConfig import *

class VoxelBase:
    """From pixels to supervoxels to megavoxels"""

    def __init__(self):
        """Constructor"""
        self.numVoxelBins = PhindConfig.numVoxelBins
        pass

    def getPixelBins(self, x, metadata, numBins):
        """Base class redirect to the static method in the VoxelFunctions class"""
        return VoxelFunctions.getPixelBins(x, metadata, numBins)
    # end getPixelBins (base class)

# end class VoxelBase




if __name__ == '__main__':
    """Unit tests"""

    pass





# end main