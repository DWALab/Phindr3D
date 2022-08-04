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
    from .VoxelBase import *
    from .SuperVoxelImage import *
except ImportError:
    from VoxelBase import *
    from SuperVoxelImage import *

class MegaVoxelImage(VoxelBase):
    def __init__(self):
        super().__init__()
        self.megaVoxelBinCenters = None # np array

    def getMegaVoxelBinCenters(self, metadata, training, pixelImage):
        # Same as getSuperVoxelBinCenters, but mega
        # required: randFieldID, metadata, supervoxels, image params (tileinfo)
        megaVoxelsforTraining = []
        superVoxel = SuperVoxelImage()
        superVoxel.getSuperVoxelBinCenters(metadata, training, pixelImage)
        for id in training.randFieldID:
            d = metadata.getImageInformation(metadata.GetImage(id))
            pixelCenters = pixelImage.pixelBinCenters
            pixelBinCenterDifferences = np.array([DataFunctions.mat_dot(pixelCenters, pixelCenters, axis=1)]).T
            print('here')
            superVoxelProfile, fgSuperVoxel = self.getTileProfiles(metadata.GetImage(id), pixelCenters, pixelBinCenterDifferences, metadata.theTileInfo, metadata)
            megaVoxelProfile, fgMegaVoxel = self.getMegaVoxelProfile(superVoxel.superVoxelBinCenters, superVoxelProfile, metadata.theTileInfo, fgSuperVoxel, training)
            if len(megaVoxelsforTraining) == 0:
                megaVoxelsforTraining = megaVoxelProfile[fgMegaVoxel]
            else:
                megaVoxelsforTraining = np.concatenate((megaVoxelsforTraining, megaVoxelProfile[fgMegaVoxel]))
        # megaVoxelBinCenters is an np array that represents the megavoxels
        self.megaVoxelBinCenters = self.getPixelBins(megaVoxelsforTraining, metadata, self.numMegaVoxelBins)


# end class MegaVoxelImage