# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of Phindr3D <https://github.com/DWALab/Phindr3D>.
#
# Phindr3D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Phindr3D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Phindr3D.  If not, see <http://www.gnu.org/licenses/>.

try:
    from .VoxelBase import *
    from .SuperVoxelImage import *
except ImportError:
    from VoxelBase import *
    from SuperVoxelImage import *

class MegaVoxelImage(VoxelBase):
    """Image managed as mega voxels, derived from VoxelBase class."""
    def __init__(self):
        """Construct base class and define additional member variable."""
        super().__init__()
        self.megaVoxelBinCenters = None # np array
    # end constructor

    def getMegaVoxelBinCenters(self, metadata, training, pixelImage, superVoxel):
        """Identify mega voxel bin centers by using getPixelBins from the base class.

        Same as getSuperVoxelBinCenters, but mega
        required: randFieldID, metadata, supervoxels, image params (tileinfo)
        superVoxel and pixelImage need to have gotten bincenters already
        """
        megaVoxelsforTraining = []
        for id in metadata.trainingSet:
            d = metadata.getImageInformation(metadata.GetImage(id))
            info = metadata.getTileInfo(d, metadata.theTileInfo)
            pixelCenters = pixelImage.pixelBinCenters
            pixelBinCenterDifferences = np.array(
                [DataFunctions.mat_dot(pixelCenters, pixelCenters, axis=1)]).T
            superVoxelProfile, fgSuperVoxel = self.getTileProfiles(
                metadata, metadata.GetImage(id), pixelCenters,
                pixelBinCenterDifferences, info)
            megaVoxelProfile, fgMegaVoxel, dump = self.getMegaVoxelProfile(
                superVoxel.superVoxelBinCenters, superVoxelProfile,
                info, fgSuperVoxel, training, analysis=False)
            if len(megaVoxelsforTraining) == 0:
                megaVoxelsforTraining = megaVoxelProfile[fgMegaVoxel]
            else:
                megaVoxelsforTraining = np.concatenate(
                    (megaVoxelsforTraining, megaVoxelProfile[fgMegaVoxel]))
        # megaVoxelBinCenters is an np array that represents the megavoxels
        # This choice of seed is associated with unit tests in VoxelGroups.py
        if metadata.Generator.seed == 1234:
            random_state = 1234
        else:
            random_state = None
        self.megaVoxelBinCenters = self.getPixelBins(
            megaVoxelsforTraining, metadata, self.numMegaVoxelBins, random_state=random_state)
    # end getMegaVoxelBinCenters
# end class MegaVoxelImage