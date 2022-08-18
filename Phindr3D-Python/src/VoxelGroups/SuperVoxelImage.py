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
    from .PixelImage import *
except ImportError:
    from VoxelBase import *
    from PixelImage import *

class SuperVoxelImage(VoxelBase):
    def __init__(self):
        super().__init__()
        self.superVoxelBinCenters = None # np array

    def getSuperVoxelBinCenters(self, metadata, training, pixelImage):
        # Same as getPixelBinCenters, but super
        # required: randFieldID, metadata, pixels, image params (tileinfo)
        pixelCenters = pixelImage.pixelBinCenters
        pixelBinCenterDifferences = np.array([DataFunctions.mat_dot(pixelCenters, pixelCenters, axis=1)]).T
        tilesForTraining = []
        for id in metadata.trainingSet:
            d = metadata.getImageInformation(metadata.GetImage(id))
            info = metadata.getTileInfo(d, metadata.theTileInfo)
            superVoxelProfile, fgSuperVoxel = self.getTileProfiles(metadata, metadata.GetImage(id), pixelCenters, pixelBinCenterDifferences, info)
            tmp = superVoxelProfile[fgSuperVoxel]
            if tmp.size != 0:
                if len(tilesForTraining) == 0:
                    tilesForTraining = tmp
                if training.superVoxelPerField > tmp.shape[0]:
                    tilesForTraining = np.concatenate((tilesForTraining, tmp))
                else:
                    tmp2Add = np.array([tmp[i, :] for i in
                                        metadata.Generator.choice(tmp.shape[0], size=training.superVoxelPerField,
                                                                  replace=False, shuffle=False)])
                    tilesForTraining = np.concatenate((tilesForTraining, tmp2Add))
            if len(tilesForTraining) == 0:
                print('\nNo foreground super-voxels found. consider changing parameters')
        self.superVoxelBinCenters = self.getPixelBins(tilesForTraining, metadata, self.numSuperVoxelBins)

# end class SuperVoxelImage