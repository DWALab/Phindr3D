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

from sklearn import cluster
import numpy as np
try:
    from ..Data import DataFunctions as dfunc
except ImportError:
    from src.Data import DataFunctions as dfunc

class VoxelFunctions:
    """Static methods for finding voxel properties. Referenced from
    https://github.com/DWALab/Phindr3D/tree/9b95aebbd2a62c41d3c87a36f1122a78a21019c8/Lib
    and
    https://github.com/SRI-RSST/Phindr3D-python/blob/ba588bc925ef72c72103738d17ea922d20771064/phindr_functions.py
    No constructor. All parameters and methods are static.
    """

    @staticmethod
    def getPixelBins(x, metadata, numBins):
        """Main function for returning bin centers of pixels, supervoxels, and mega voxels
            x - m x n (m is number of observations, n is number of channels/category fractions
            numBins - number of categories"""
        Generator = metadata.Generator
        m = x.shape[0]
        if m > 50000:
            samSize = 50000
        else:
            samSize = m
        if m > samSize:
            numRandRpt = 10
            binCenters = np.zeros((numBins, x.shape[1], numRandRpt))
            sumD = np.zeros(numRandRpt)
            for iRandCycle in range(0, numRandRpt):
                randpermX = np.array([x[j] for j in Generator.choice(m, size=samSize, replace=False, shuffle=False)])
                kmeans = cluster.KMeans(n_clusters=numBins, init='k-means++', n_init=100, max_iter=100).fit(
                    randpermX)  # max_iter used to be 100. changed because bin-centers don't always match up to real values.
                binCenters[:, :, iRandCycle] = kmeans.cluster_centers_
                temp1 = np.add(
                    np.array([dfunc.mat_dot(binCenters[:, :, numRandRpt - 1], binCenters[:, :, numRandRpt - 1], axis=1)]).T,
                    dfunc.mat_dot(x, x, axis=1)).T  # still not sure which one of this or the next should be transposed
                temp2 = 2 * (x @ binCenters[:, :, numRandRpt - 1].T)
                a = (temp1 - temp2)
                sumD[iRandCycle] = np.sum(np.amin(a, axis=1))
            minDis = np.argmin(sumD)
            binCenters = binCenters[:, :, minDis]
        else:
            kmeans = cluster.KMeans(n_clusters=numBins, init='k-means++', n_init=100, max_iter=100).fit(
                x)  # max iter used to be 100
            binCenters = kmeans.cluster_centers_
        return np.abs(binCenters)
    # end getPixelBins

    @staticmethod
    def getTileProfiles(imageObject, pixelBinCenters, tileInfo, numVoxelBins,
        intensityNormPerTreatment=False, allTreatmentTypes=None,
        computeTAS=False): # , param, analysis=False):
        """Tile profiles. Called in extractImageLevelTextureFeatures, getMegaVoxelBinCenters,
            called in getSuperVoxelBinCenters.
            Computes low level categorical features for supervoxels
            function assigns categories for each pixel, computes supervoxel profiles for each supervoxel
            Inputs:

            - an Image object (with Stack and Channel member objects)
            - pixelBinCenters - Location of pixel categories: number of bins x number of channels
            - tileInfo - a TileInfo object
            - intensityNormPerTreatment - whether the treatment is considered when analyzing data

            ii: current image id
            % Output:
            % superVoxelProfile: number of supervoxels by number of supervoxelbins plus a background
            % fgSuperVoxel: Foreground supervoxels - At lease one of the channels
            % should be higher than the respective threshold
            % TASScores: If TAS score is selected
            """
        errorVal = (None, None)
        numChannels = imageObject.GetNumChannels()
        numTilesXY = int((tileInfo.croppedX * tileInfo.croppedY) / (tileInfo.tileX * tileInfo.tileY))
        zEnd = -tileInfo.zOffsetEnd
        if zEnd == -0:
            zEnd = None
        zStack = imageObject.stackLayers
        zStackKeys = list(zStack.keys())
        # keep z stacks that are divisible by stack count
        slices = zStackKeys[tileInfo.zOffsetStart:zEnd]
        sliceCounter = 0
        startVal = 0
        endVal = numTilesXY
        startCol = 0
        endCol = tileInfo.tileX * tileInfo.tileY

        if intensityNormPerTreatment:
            # index of the treatment for this image in the list of all treatments
            # if the treatment type is not found (or there are no treatments), return error
            try:
                grpVal = allTreatmentTypes.index(imageObject.GetTreatment()[0])
            except (ValueError, IndexError):
                return errorVal
        superVoxelProfile = np.zeros((tileInfo.numSuperVoxels, numVoxelBins+1))
        fgSuperVoxel = np.zeros(tileInfo.numSuperVoxels)
        if computeTAS:
            categoricalImage = np.zeros((tileInfo.croppedX, tileInfo.croppedY, tileInfo.croppedZ))
        # loop over file names and extract super voxels
        # tmpData holds the binned pixel image (ONE LAYER OF SUPERVOXELS AT A TIME.)
        # dimensions: number of supervoxels in a 2D cropped image x number of voxels in a supervoxel.
        tmpData = np.zeros((numTilesXY, int(tileInfo.tileX * tileInfo.tileY * tileInfo.tileZ)))
        print(tmpData)
        for iImages, zslice in enumerate(slices):
            sliceCounter += 1
            # just one slice in all channels
            croppedIM = np.zeros((tileInfo.origX, tileInfo.origY, numChannels))
            for jChan in range(numChannels):
                try:
                    if intensityNormPerTreatment:
                        pass
                        # dfunc.rescaleIntensity()



                    else:
                        pass


                except (ValueError, IndexError):
                    return errorVal
            xEnd = -tileInfo.xOffsetEnd
            if xEnd == -0:
                # if the end index is -0, you just index from 1 to behind 1 and get an empty array.
                # Change to 0 if the dimOffsetEnd value is 0.
                xEnd = None
            yEnd = -tileInfo.yOffsetEnd
            if yEnd == -0:
                yEnd = None

            # crop image to right dimensions for calculating supervoxels
            # z portion of the offset has already been done by not loading the wrong slices
            croppedIM = croppedIM[tileInfo.xOffsetStart:xEnd, tileInfo.yOffsetStart:yEnd, :]







    # end getTileProfiles


# end VoxelFunctions


