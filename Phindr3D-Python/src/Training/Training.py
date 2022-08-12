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

"""
Ok, when are things supposed to happen?

so metadata gets loaded, and then?







"""


from .TrainingFunctions import *
from ..PhindConfig.PhindConfig import *


class Training:
    """This class ...
       Static methods that draw closely from transliterations of the MATLAB functions
       can be found in the SegmentationFunctions class."""

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

        # params to be defined later (in training functions)
        # self.intensityThresholdValues = None  #gets computed at metadata loading stage
        # self.randZForTraining = None          #gets computed on a per-image basis during category making
        # self.randFieldID = None               #gets determined at metadata loading stage for scaling and thresholding
        # self.randTrainingPerTreatment = None  #not sure about this one (intensity threshold values and scaling factors should already reflect training per treatment if chosen)

    # end constructor




# end class Training




if __name__ == '__main__':
    """Tests of the Training class that can be run directly."""



# end main