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








    # Will this go here? Will it go to one of the derived classes? I don't know.
    def getMegaVoxelProfile(self, superVoxelBinCenters, tileProfile,
        tileInfo, fgSuperVoxel, analysis=False):
        """called in extractImageLevelTextureFeatures and getMegaVoxelBinCenters"""
        # Create local copies of external variables (easier to merge code)
        showImage = PhindConfig.showImage
        textureFeatures = PhindConfig.textureFeatures
        temp1 = np.array([dfunc.mat_dot(superVoxelBinCenters, superVoxelBinCenters, axis=1)]).T
        temp2 = dfunc.mat_dot(tileProfile[fgSuperVoxel], tileProfile[fgSuperVoxel], axis=1)
        a = np.add(temp1, temp2).T - 2*(tileProfile[fgSuperVoxel] @ superVoxelBinCenters.T)
        minDis = np.argmin(a, axis=1) + 1 #mindis+1 here
        x = np.zeros(tileProfile.shape[0], dtype='uint8') #x is the right shape
        x[fgSuperVoxel] = minDis
        #had to change x shape here from matlab form to more numpy like shape.
        x = np.reshape(x, (int(tileInfo.croppedZ/tileInfo.tileZ),
            int(tileInfo.croppedX/tileInfo.tileX), int(tileInfo.croppedY/tileInfo.tileY))) #new shape (z, x, y)

        if showImage:




        # end if

        if analysis and textureFeatures:
            pass


        else:

        # end if


    # end getMegaVoxelProfile






# end class VoxelBase




if __name__ == '__main__':
    """Unit tests"""

    pass





# end main