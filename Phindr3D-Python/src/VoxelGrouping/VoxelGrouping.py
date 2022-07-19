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

from VoxelGroupingFunctions import VoxelGroupingFunctions
from ..PhindConfig import *

class VoxelGrouping(VoxelGroupingFunctions):
    """Not sure what this class is for yet"""

    def __init__(self):
        """ClusterStuff constructor"""

        initial_params = PhindConfig()
        self.tilex = None
        self.tiley = None
        self.tilez = None
        self.megaVoxelTileX = None
        self.megaVoxelTileY = None
        self.megaVoxelTileZ = None
        self.numSuperVoxelZ = None
        self.numMegaVoxelsXY = None
        self.numMegaVoxels = None
        self.pixelBinCenters = None
        self.pixelBinCenterDifferences = None
        self.superVoxelBinCenters = None
        self.xOffsetStart = None
        self.xOffsetEnd = None
        self.yOffsetStart = None
        self.yOffsetEnd = None
        self.zOffsetStart = None
        self.zOffsetEnd = None
        self.croppedX = None
        self.croppedY = None
        self.croppedZ = None
        self.origX = None
        self.origY = None
        self.origZ = None
        self.superVoxelXOffsetStart = None
        self.superVoxelXOffsetEnd = None
        self.superVoxelXAddStart = None
        self.superVoxelXAddEnd = None
        self.superVoxelYAddStart = None
        self.superVoxelYAddEnd = None
        self.superVoxelZAddStart = None
        self.superVoxelZAddEnd = None
        self.superVoxelYOffsetStart = None
        self.superVoxelYOffsetEnd = None
        self.superVoxelZOffsetStart = None
        self.superVoxelZOffsetEnd = None
        self.numSuperVoxels = None
        self.numSuperVoxelsXY = None
        pass

# end class VoxelGrouping




if __name__ == '__main__':
    """Not sure what this will do yet"""

    pass





# end main