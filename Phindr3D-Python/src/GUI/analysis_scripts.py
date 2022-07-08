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
#script modified/taken from previous PHINDR functions...

#NOTE: param.intensityNormPerTreatment if True max-min normalization based on treatment max, min
def getImageThreshold(IM):
    """called in getIndividualChannelThreshold"""
    maxBins = 256
    freq, binEdges = np.histogram(IM.flatten(), bins=maxBins)
    binCenters = binEdges[:-1] + np.diff(binEdges) / 2
    meanIntensity = np.mean(IM.flatten())
    numThresholdParam = len(freq)
    binCenters -= meanIntensity
    den1 = np.sqrt((binCenters ** 2) @ freq.T)
    numAllPixels = np.sum(
        freq)  # freq should hopefully be a 1D vector so summ of all elements should be right.
    covarMat = np.zeros(numThresholdParam)
    for iThreshold in range(numThresholdParam):
        numThreshPixels = np.sum(freq[binCenters > binCenters[iThreshold]])
        den2 = np.sqrt((((numAllPixels - numThreshPixels) * (numThreshPixels)) / numAllPixels))
        if den2 == 0:
            covarMat[iThreshold] = 0  # dont want to select these, also want to avoid nans
        else:
            covarMat[iThreshold] = (binCenters @ (freq * (binCenters > binCenters[iThreshold])).T) / (
                        den1 * den2)  # i hope this is the right mix of matrix multiplication and element-wise stuff.
    imThreshold = np.argmax(covarMat)  # index makes sense here.
    imThreshold = binCenters[imThreshold] + meanIntensity
    return imThreshold

def getImageWithSVMVOverlay(IM, param, type):
    """
    I assume this means get image with superVoxel or megaVoxel overlay.
    % param.tileX = 10;
    % param.tileY = 10;
    % param.megaVoxelTileX = 5;
    % param.megaVoxelTileY = 5;
    """
    xOffset = np.mod(IM.shape[0], param.tileX);
    yOffset = np.mod(IM.shape[1], param.tileY);
    param.croppedX = IM.shape[0] - xOffset;
    param.croppedY = IM.shape[1] - yOffset;
    superVoxelXOffset = np.mod(param.croppedX/ param.tileX, param.megaVoxelTileX);
    superVoxelYOffset = np.mod(param.croppedY/ param.tileY, param.megaVoxelTileY);
    spX = int((param.croppedX/ param.tileX));
    spY = int((param.croppedY/ param.tileY));
    tmpX = int((param.croppedX/ param.tileX) + superVoxelXOffset);
    tmpY = int((param.croppedY/ param.tileY) + superVoxelYOffset);

    if type == 'SV':
        IM[range(0,IM.shape[0],int(spX/param.megaVoxelTileX)), :,:] = (0.7, 0.7, 0.7, 1.0)
        IM[:, range(0,IM.shape[1], int(spY/param.megaVoxelTileY)),:] = (0.7, 0.7, 0.7, 1.0)
        IM[range(1,IM.shape[0],int(spX/param.megaVoxelTileX)), :,:] = (0.7, 0.7, 0.7, 1.0)
        IM[:, range(1,IM.shape[1], int(spY/param.megaVoxelTileY)),:] = (0.7, 0.7, 0.7, 1.0)

    else:
        IM[range(0,IM.shape[0],tmpX), :,:] = (1.0, 1.0, 1.0, 1.0)
        IM[:, range(0,IM.shape[1],tmpY),:] = (1.0, 1.0, 1.0, 1.0)
        IM[range(1,IM.shape[0],tmpX), :,:] = (1.0, 1.0, 1.0, 1.0)
        IM[:, range(1,IM.shape[1],tmpY),:] = (1.0, 1.0, 1.0, 1.0)

    return IM