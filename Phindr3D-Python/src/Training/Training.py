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
from ..PhindConfig import *


class Training(TrainingFunctions):
    """This class ...
       Static methods that draw closely from transliterations of the MATLAB functions
       can be found in the SegmentationFunctions class."""

    def __init__(self):
        """Training class constructor"""
        # params defined in Phind Config
        initial_params = PhindConfig()
        self.intensityThresholdTuningFactor = initial_params.intensityThresholdTuningFactor
        self.minQuantileScaling = initial_params.minQuantileScaling
        self.maxQuantileScaling = initial_params.maxQuantileScaling
        self.randTrainingSuperVoxel = initial_params.randTrainingSuperVoxel
        self.superVoxelThresholdTuningFactor = initial_params.superVoxelThresholdTuningFactor
        self.megaVoxelThresholdTuningFactor = initial_params.megaVoxelThresholdTuningFactor
        self.randTrainingFields = initial_params.randTrainingFields
        self.pixelsPerImage = initial_params.pixelsPerImage
        self.trainingPerColumn = initial_params.trainingPerColumn
        self.superVoxelPerField = initial_params.superVoxelPerField

        # params to be defined later (in training functions)
        self.intensityThresholdValues = None
        self.randZForTraining = None
        self.randFieldID = None
        self.randTrainingPerTreatment = None

    # end constructor




# end class Training




if __name__ == '__main__':
    """Tests of the Training class that can be run directly."""



# end main