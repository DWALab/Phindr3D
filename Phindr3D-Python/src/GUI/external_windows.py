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
from .windows import *

class external_windows():
    def buildExtractWindow(self):
        return extractWindow()

    def buildResultsWindow(self, color, metadata):
        return resultsWindow(color, metadata)

    def buildParamWindow(self, metaheader, supercoords, svcategories, megacoords, mvcategories, voxelnum, trainingnum, bg, norm, conditiontrain, trainingcol, treatcol):
        return paramWindow(metaheader, supercoords, svcategories, megacoords, mvcategories, voxelnum, trainingnum, bg, norm, conditiontrain, trainingcol, treatcol)

    def buildSegmentationWindow(self, metadata):
        return segmentationWindow(metadata)

    def buildColorchannelWindow(self):
        return colorchannelWindow()

    def buildRegexWindow(self):
        return regexWindow()

