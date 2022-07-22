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
        initial_params = PhindConfig()
        self.numVoxelBins = initial_params.numVoxelBins
        pass

    ## Main function for returning bin centers of pixels, supervoxels, and mega voxels
    ## x - m x n (m is number of observations, n is number of channels/category fractions
    ## numBins - number of categories
    def getPixelBins(x, numBins):
        pass

# end class VoxelBase




if __name__ == '__main__':
    """Not sure what this will do yet"""

    pass





# end main