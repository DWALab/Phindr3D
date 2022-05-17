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

class PhindConfig:
    """Static configuration parameters for Phindr3D. Modified from
       https://github.com/SRI-RSST/Phindr3D-python/blob/e902f6e8015a5a091667c83eef4dab61dbfd79b6/phindr3d.ipynb
       These may move from this class if they require modification."""
    # No constructor. All parameters and methods are static

    @staticmethod
    def random_cmap(map_len=40, black_background=True):
        """
        This static method creates a random color map, useful in segmentation maps.
        :param map_len: optional. length of color map. default is 256.

        :return: random color map.
        """
        from matplotlib import colors
        from numpy import random
        temp_cmap = random.rand(map_len, 3)
        if black_background:
            temp_cmap[0] = 0
        return colors.ListedColormap(temp_cmap)
    # end random_cmap

    # Super-Voxel dimensions
    tileX = 10
    tileY = 10
    tileZ = 3
    # Mega-Voxel dimensions
    megaVoxelTileX = 5
    megaVoxelTileY = 5
    megaVoxelTileZ = 2
    # Number of categories for binning
    numVoxelBins = 20
    numSuperVoxelBins = 15
    numMegaVoxelBins = 30
    # Foreground thresholds
    intensityThresholdTuningFactor = 0.5
    superVoxelThresholdTuningFactor = 0.5
    megaVoxelThresholdTuningFactor = 0.5
    # Training parameters
    randTrainingSuperVoxel = 10000
    pixelsPerImage = 200
    randTrainingFields = 5
    randTrainingPerTreatment = 1
    intensityNormPerTreatment = False
    # Visualization
    showBinCenters = False
    showImage = False
    showChannels = False # show individual channels instead of rgb images.

    # Include texture features of Mega Voxel image
    textureFeatures = True

    # Misc.
    minQuantileScaling = 0.5
    maxQuantileScaling = 0.5
    countBackground = False
    startZPlane = 1
    endZPlane = 500
    numRemoveZStart = 1
    numRemoveZEnd = 1
    computeTAS = 0
    trainingPerColumn = False
    # treatmentColNameForNormalization = ''
    # imageTreatments = []
    # allTreatments = []
    # trainingColforImageCategories = []
    superVoxelPerField = randTrainingSuperVoxel//randTrainingFields
    lowerbound = [0, 0, 0]
    upperbound = [1, 1, 1]
    numChannels = 3

    svcolormap = random_cmap(map_len=numSuperVoxelBins+1)
    mvcolormap = random_cmap(map_len=numMegaVoxelBins+1)

# end class PhindConfig

