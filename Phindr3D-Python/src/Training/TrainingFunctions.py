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

import numpy as np

class TrainingFunctions:
    """Static methods for training. Referenced from
    https://github.com/DWALab/Phindr3D/tree/9b95aebbd2a62c41d3c87a36f1122a78a21019c8/Lib
    and
    https://github.com/SRI-RSST/Phindr3D-python/blob/ba588bc925ef72c72103738d17ea922d20771064/phindr_functions.py
    No constructor. All parameters and methods are static.
    """

    # Functions for training, these functions can be found from Teo's code in
    # https://github.com/SRI-RSST/Phindr3D-python/blob/main/phindr_functions.py
    # Work on copying functionality later. For now, functions do nothing
    def getImageThreshold(self):
        """Currently implemented in Metadata.py"""
        pass

    def getImageThresholdValues(self):
        """Currently implemented in Metadata.py"""
        pass

    def getIndividualChannelThreshold(self):
        """Currently implemented in Metadata.py"""
        pass

    def getScalingFactorForImages(self):
        """Currently implemented in Metadata.py"""
        pass

    def getTrainingFields(self):
        """Currently implemented in Metadata.py"""
        pass

    def rescaleIntensity(self, im, low=0, high=1):
        im = im.astype(np.float64)
        diffIM = high - low
        im = (im - low)/diffIM
        im[im>1] = 1
        im[im<0] = 0
        return im


# end TrainingFunctions


