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

from ..PhindConfig.PhindConfig import *

class Training:
    def __init__(self):
        """Training class constructor"""
        # params defined in Phind Config
        self.intensityThresholdTuningFactor = PhindConfig.intensityThresholdTuningFactor
        self.minQuantileScaling = PhindConfig.minQuantileScaling
        self.maxQuantileScaling = PhindConfig.maxQuantileScaling
        self.randTrainingSuperVoxel = PhindConfig.randTrainingSuperVoxel
        self.superVoxelThresholdTuningFactor = PhindConfig.superVoxelThresholdTuningFactor
        self.megaVoxelThresholdTuningFactor = PhindConfig.megaVoxelThresholdTuningFactor
        self.randTrainingFields = PhindConfig.randTrainingFields
        self.pixelsPerImage = PhindConfig.pixelsPerImage
        self.trainingPerColumn = PhindConfig.trainingPerColumn
        self.superVoxelPerField = PhindConfig.superVoxelPerField
    # end constructor

# end class Training
