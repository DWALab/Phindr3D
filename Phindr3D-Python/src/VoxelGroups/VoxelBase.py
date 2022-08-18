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

import imageio.v2 as io

try:
    from .VoxelFunctions import *
except ImportError:
    from VoxelFunctions import *

try:
    from ..PhindConfig.PhindConfig import *
except ImportError:
    from src.PhindConfig.PhindConfig import *

import matplotlib.pyplot as plt
#from mahotas.features import texture
import mahotas as mt

class VoxelBase:
    """From pixels to supervoxels to megavoxels"""

    def __init__(self):
        """Constructor"""
        self.numVoxelBins = PhindConfig.numVoxelBins
        self.numSuperVoxelBins = PhindConfig.numSuperVoxelBins
        self.numMegaVoxelBins = PhindConfig.numMegaVoxelBins
        self.textureFeatures = PhindConfig.textureFeatures

    def getPixelBins(self, x, metadata, numBins):
        """Base class redirect to the static method in the VoxelFunctions class"""
        return VoxelFunctions.getPixelBins(x, metadata, numBins)
    # end getPixelBins (base class)

    def getTileProfiles(self, metadata, imageObject, pixelBinCenters, pixelBinCenterDifferences, theTileInfo):
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
        # Create local copies of external variables (easier to merge code)
        allTreatmentTypes = metadata.GetTreatmentTypes()
        intensityNormPerTreatment = metadata.intensityNormPerTreatment
        intensityThreshold = metadata.intensityThreshold
        lowerbound = metadata.lowerbound
        upperbound = metadata.upperbound
        computeTAS = PhindConfig.computeTAS
        showImage = PhindConfig.showImage
        showChannels = PhindConfig.showChannels
        countBackground = PhindConfig.countBackground
        superVoxelThresholdTuningFactor = PhindConfig.superVoxelThresholdTuningFactor
        numChannels = imageObject.GetNumChannels()
        numVoxelBins = self.numVoxelBins
        #
        numTilesXY = int((theTileInfo.croppedX * theTileInfo.croppedY) / (theTileInfo.tileX * theTileInfo.tileY))
        zEnd = -theTileInfo.zOffsetEnd
        if zEnd == -0:
            zEnd = None
        zStack = imageObject.stackLayers
        zStackKeys = list(zStack.keys())
        # keep z stacks that are divisible by stack count
        slices = zStackKeys[theTileInfo.zOffsetStart:zEnd]
        sliceCounter = 0
        startVal = 0
        endVal = numTilesXY
        startCol = 0
        endCol = theTileInfo.tileX * theTileInfo.tileY

        if intensityNormPerTreatment:
            # index of the treatment for this image in the list of all treatments
            # if the treatment type is not found (or there are no treatments), return error
            try:
                grpVal = allTreatmentTypes.index(imageObject.GetTreatment()[0])
            except (ValueError, IndexError):
                return errorVal
        # end if
        superVoxelProfile = np.zeros((theTileInfo.numSuperVoxels, numVoxelBins+1))
        fgSuperVoxel = np.zeros(theTileInfo.numSuperVoxels)
        if computeTAS:
            categoricalImage = np.zeros((theTileInfo.croppedX, theTileInfo.croppedY, theTileInfo.croppedZ))
        # loop over file names and extract super voxels
        # tmpData holds the binned pixel image (ONE LAYER OF SUPERVOXELS AT A TIME.)
        # dimensions: number of supervoxels in a 2D cropped image x number of voxels in a supervoxel.
        tmpData = np.zeros((numTilesXY, int(theTileInfo.tileX * theTileInfo.tileY * theTileInfo.tileZ)))
        for iImages, zslice in enumerate(slices):
            sliceCounter += 1
            # just one slice in all channels
            croppedIM = np.zeros((theTileInfo.origX, theTileInfo.origY, numChannels))
            for jChan in range(numChannels):
                try:
                    stackIndex = list(imageObject.stackLayers.keys())[iImages]
                    theStack = imageObject.stackLayers[stackIndex]
                    channelIndex = list(theStack.channels.keys())[jChan]
                    theChannel = theStack.channels[channelIndex]
                    imFileName = theChannel.channelpath
                except (IndexError, AttributeError):
                    return errorVal
                IM = io.imread(imFileName)
                try:
                    if intensityNormPerTreatment:
                        croppedIM[:, :, jChan] = dfunc.rescaleIntensity(IM,
                            low=lowerbound[grpVal, jChan],
                            high=upperbound[grpVal, jChan])
                    else:
                        croppedIM[:, :, jChan] = dfunc.rescaleIntensity(IM,
                            low=lowerbound[jChan],
                            high=upperbound[jChan])
                except (ValueError, IndexError):
                    return errorVal
            xEnd = -theTileInfo.xOffsetEnd
            if xEnd == -0:
                # if the end index is -0, you just index from 1 to behind 1 and get an empty array.
                # Change to 0 if the dimOffsetEnd value is 0.
                xEnd = None
            yEnd = -theTileInfo.yOffsetEnd
            if yEnd == -0:
                yEnd = None
            # crop image to right dimensions for calculating supervoxels
            # z portion of the offset has already been done by not loading the wrong slices
            croppedIM = croppedIM[theTileInfo.xOffsetStart:xEnd, theTileInfo.yOffsetStart:yEnd, :]

            if showImage:
                if showChannels or numChannels != 3:
                    fig, ax = plt.subplots(1, int(numChannels))
                    for i in range(numChannels):
                        ax[i].set_title(f'Channel {i+1}')
                        ax[i].imshow(croppedIM[:, :, i], 'gray')
                        ax[i].set_xticks([])
                        ax[i].set_yticks([])
                elif numChannels == 3:
                    plt.figure()
                    title = f'slice {zslice}'
                    plt.title(title)
                    # leaving it in multichannel gives rgb correctly for 3 channel image.
                    # WILL Fail for numChannel != 3
                    plt.imshow(croppedIM)
                plt.show()
            # end if

            # flatten image, keeping channel dimension separate
            x = np.reshape(croppedIM, (theTileInfo.croppedX*theTileInfo.croppedY, numChannels))
            # want to be greater than threshold in at least 1 channel
            fg = np.sum(x > intensityThreshold, axis=1) >= 1
            pixelCategory = np.argmin(np.add(pixelBinCenterDifferences, dfunc.mat_dot(x[fg,:], x[fg,:], axis=1)).T - 2*(x[fg,:] @ pixelBinCenters.T), axis=1) + 1
            x = np.zeros(theTileInfo.croppedX*theTileInfo.croppedY, dtype='uint8')
            # assign voxel bin categories to the flattened array
            x[fg] = pixelCategory

            ## uncomment for testing if needed.
            # x_show = np.reshape(x, (theTileInfo.croppedX, param.croppedY))
            # np.savetxt(r'<location>\pytvoxelim.csv', x_show, delimiter=',')

            #here, x can be reshaped to croppedX by croppedY and will give the map
            # of pixel assignments for the image slice
            if computeTAS:
                categoricalImage[:, :, iImages] = np.reshape(x, theTileInfo.croppedX, theTileInfo.croppedY)
            # del fg, croppedIM, pixelCategory #not 100 on why to delete al here since things
            # would just be overwritten anyway, but why not right, also, some of the variables
            # to clear where already commented out so I removed them from the list
            if sliceCounter == theTileInfo.tileZ:
                # add the tmpData that has been accumulating for the past  to the fgsupervoxel
                fgSuperVoxel[startVal:endVal] = (np.sum(tmpData != 0, axis=1) / tmpData.shape[
                    1]) >= superVoxelThresholdTuningFactor
                for i in range(0, numVoxelBins + 1):
                    # 0 indicates background
                    superVoxelProfile[startVal:endVal, i] = np.sum(tmpData == i, axis=1)
                # reset for next image
                sliceCounter = int(0)
                startVal += numTilesXY
                endVal += numTilesXY
                startCol = 0
                endCol = theTileInfo.tileX * theTileInfo.tileY
                tmpData = np.zeros((numTilesXY, theTileInfo.tileX * theTileInfo.tileY * theTileInfo.tileZ))
            else:
                tmpData[:, startCol:endCol] = dfunc.im2col(np.reshape(x,
                    (theTileInfo.croppedX, theTileInfo.croppedY)),
                    (theTileInfo.tileX, theTileInfo.tileY)).T
                startCol += (theTileInfo.tileX * theTileInfo.tileY)
                endCol += (theTileInfo.tileX * theTileInfo.tileY)

        if not countBackground:
            superVoxelProfile = superVoxelProfile[:, 1:]
        superVoxelProfile = np.divide(superVoxelProfile, np.array([np.sum(superVoxelProfile, axis=1)]).T) #dont worry about divide by zero errors, they are supposed to happen here!
        superVoxelProfile[superVoxelProfile == np.nan] = 0
        fgSuperVoxel = fgSuperVoxel.astype(bool)
        ##fgSuperVoxel used to be fgSuperVoxel.T
        return superVoxelProfile, fgSuperVoxel
    # end getTileProfiles

    def getMegaVoxelProfile(self, superVoxelBinCenters, tileProfile, tileInfo, fgSuperVoxel, training, analysis=False):
        """called in extractImageLevelTextureFeatures and getMegaVoxelBinCenters"""
        # Create local copies of external variables (easier to merge code)
        errorVal = (None, None)
        showImage = PhindConfig.showImage
        countBackground = PhindConfig.countBackground
        svcolormap = PhindConfig.svcolormap
        temp1 = np.array([dfunc.mat_dot(superVoxelBinCenters, superVoxelBinCenters, axis=1)]).T
        temp2 = dfunc.mat_dot(tileProfile[fgSuperVoxel], tileProfile[fgSuperVoxel], axis=1)
        a = np.add(temp1, temp2).T - 2*(tileProfile[fgSuperVoxel] @ superVoxelBinCenters.T)
        minDis = np.argmin(a, axis=1) + 1 #mindis+1 here
        x = np.zeros(tileProfile.shape[0], dtype='uint8') #x is the right shape
        x[fgSuperVoxel] = minDis
        #had to change x shape here from matlab form to more numpy like shape.
        x = np.reshape(x, (int(tileInfo.croppedZ/tileInfo.tileZ),
            int(tileInfo.croppedX/tileInfo.tileX), int(tileInfo.croppedY/tileInfo.tileY))) #new shape (z, x, y)

        if showImage:
            for i in range(x.shape[0]):
                plt.figure()
                title = f'Supervoxel image'
                plt.title(title)
                plt.imshow(x[i, :, :], svcolormap)
                plt.colorbar()
                plt.show()
        # end if

        if analysis:
            sv_image = np.reshape(x,
                (int(tileInfo.croppedZ / tileInfo.tileZ),
                 int(tileInfo.croppedX / tileInfo.tileX),
                 int(tileInfo.croppedY / tileInfo.tileY)))
            tileInfo.numSuperVoxelZ = int(tileInfo.croppedZ / tileInfo.tileZ)
            total_mean_textures = np.full((tileInfo.numSuperVoxelZ, 4), np.nan)
            for i in range(sv_image.shape[0]):
                texture_features = np.full((2, 13), np.nan)
                try:
                    texture_features[0, :] = mt.features.haralick(sv_image[i, :, :],
                        distance=1, ignore_zeros=True, return_mean=True)
                except ValueError:
                    return errorVal
                try:
                    texture_features[1, :] = mt.features.haralick(sv_image[i, :, :],
                        distance=2, ignore_zeros=True, return_mean=True)
                except ValueError:
                    return errorVal
                texture_features = texture_features[:, [0, 8, 11, 12]]
                texture_features = texture_features[~np.isnan(texture_features).any(axis=1), :]
                if len(texture_features) > 1:
                    texture_features = np.mean(texture_features, axis=0)
                if texture_features.size > 0:
                    total_mean_textures[i, :] = texture_features
            # end for
            total_mean_textures = total_mean_textures[~np.isnan(total_mean_textures).any(axis=1), :]
            textureFeatures = np.mean(total_mean_textures, axis=0)
            try:
                if texture_features.size == 0:
                    self.texture_features = False
                    print(f'Texture feature extraction failed. continuing with default phindr3D')
                    textureFeatures = None
            except AttributeError:
                return errorVal
        else:
            textureFeatures = None
        # end if

        #pad first dimension
        x = np.concatenate([ np.zeros((tileInfo.superVoxelZAddStart, x.shape[1], x.shape[2])),
            x, np.zeros((tileInfo.superVoxelZAddEnd, x.shape[1], x.shape[2])) ], axis=0) #new (z, x, y) shape
        #pad second dimension
        x = np.concatenate([ np.zeros((x.shape[0], tileInfo.superVoxelXAddStart, x.shape[2])),
            x, np.zeros((x.shape[0], tileInfo.superVoxelXAddEnd, x.shape[2])) ], axis=1) #new (z, x, y) shape
        #pad third dimension
        x = np.concatenate([ np.zeros((x.shape[0], x.shape[1], tileInfo.superVoxelYAddStart)),
            x, np.zeros((x.shape[0], x.shape[1], tileInfo.superVoxelYAddEnd)) ], axis=2) #for new (z, x, y) shape
        x = x.astype(np.uint8)
        tileInfo.numMegaVoxelX = x.shape[1]//tileInfo.megaVoxelTileX
        tileInfo.numMegaVoxelY = x.shape[2]//tileInfo.megaVoxelTileY
        tileInfo.numMegaVoxelZ = x.shape[0]//tileInfo.megaVoxelTileZ
        tileInfo.numMegaVoxelsXY = int(x.shape[1] * x.shape[2] / (tileInfo.megaVoxelTileY * tileInfo.megaVoxelTileX)) #for new shape
        tileInfo.numMegaVoxels = int((tileInfo.numMegaVoxelsXY*x.shape[0])/tileInfo.megaVoxelTileZ)
        sliceCounter = 0
        startVal = 0
        endVal = tileInfo.numMegaVoxelsXY
        try:
             megaVoxelProfile = np.zeros((tileInfo.numMegaVoxels, self.numSuperVoxelBins+1))
        except Exception as e:
            print(e)
            return errorVal
        fgMegaVoxel = np.zeros(tileInfo.numMegaVoxels)
        tmpData = np.zeros((tileInfo.numMegaVoxelsXY,
            int(tileInfo.megaVoxelTileX*tileInfo.megaVoxelTileY*tileInfo.megaVoxelTileZ)))
        startCol = 0
        endCol = (tileInfo.megaVoxelTileX*tileInfo.megaVoxelTileY)

        for iSuperVoxelImagesZ in range(0, x.shape[0]):
            sliceCounter += 1
            # changed which axis is used to iterate through z.
            tmpData[:, startCol:endCol] = dfunc.im2col(x[iSuperVoxelImagesZ, :, :],
                (tileInfo.megaVoxelTileX, tileInfo.megaVoxelTileY)).T
            startCol += (tileInfo.megaVoxelTileX * tileInfo.megaVoxelTileY)
            endCol += (tileInfo.megaVoxelTileX * tileInfo.megaVoxelTileY)

            if sliceCounter == tileInfo.megaVoxelTileZ:
                fgMegaVoxel[startVal:endVal] \
                    = (np.sum(tmpData!= 0, axis=1)/tmpData.shape[1]) >= training.megaVoxelThresholdTuningFactor
                for i in range(0, self.numSuperVoxelBins+1):
                    # value of zeros means background supervoxel
                    megaVoxelProfile[startVal:endVal, i] = np.sum(tmpData == i, axis=1)
                sliceCounter = 0
                tmpData = np.zeros((tileInfo.numMegaVoxelsXY,
                    tileInfo.megaVoxelTileX*tileInfo.megaVoxelTileY*tileInfo.megaVoxelTileZ))
                startCol = 0
                endCol = (tileInfo.megaVoxelTileX*tileInfo.megaVoxelTileY)
                startVal += tileInfo.numMegaVoxelsXY
                endVal += tileInfo.numMegaVoxelsXY
        # end for

        if not countBackground:
            megaVoxelProfile = megaVoxelProfile[:, 1:]
        megaVoxelProfile = np.divide(megaVoxelProfile,
            np.array([np.sum(megaVoxelProfile, axis=1)]).T) #dont worry about divide by zero here either
        fgMegaVoxel = fgMegaVoxel.astype(bool)

        return megaVoxelProfile, fgMegaVoxel, textureFeatures
    # end getMegaVoxelProfile

    def getImageProfile(self, megaVoxelBinCenters, megaVoxelProfile, tileInfo, fgMegaVoxel):
        """provides multi-parametric representation of image based on megavoxel categories.
            called in extractImageLevelTextureFeatures"""
        errorVal = (None, None)
        showImage = PhindConfig.showImage
        countBackground = PhindConfig.countBackground
        mvcolormap = PhindConfig.mvcolormap
        tmp1 = np.array([dfunc.mat_dot(megaVoxelBinCenters, megaVoxelBinCenters, axis=1)]).T
        tmp2 = dfunc.mat_dot(megaVoxelProfile[fgMegaVoxel], megaVoxelProfile[fgMegaVoxel], axis=1)
        a = np.add(tmp1, tmp2).T - (2 * (megaVoxelProfile[fgMegaVoxel] @ megaVoxelBinCenters.T))
        minDis = np.argmin(a, axis=1) + 1
        x = np.zeros(megaVoxelProfile.shape[0], dtype='uint8')
        x[fgMegaVoxel] = minDis
        numbins = self.numMegaVoxelBins
        tmp = np.zeros(numbins + 1)
        for i in range(0, numbins + 1):
            tmp[i] = np.sum(x[fgMegaVoxel] == (i))
        imageProfile = tmp
        if showImage:
            mv_show = np.reshape(x, (tileInfo.numMegaVoxelZ, tileInfo.numMegaVoxelX, tileInfo.numMegaVoxelY))
            for i in range(mv_show.shape[0]):
                plt.figure()
                title = f'Megavoxel image'
                plt.title(title)
                plt.imshow(mv_show[i, :, :], mvcolormap)
                plt.colorbar()
                plt.show()

        # In phindr_functions.py, there were several lines commented out here
        # They were inside an if statement, if param.textureFeatures

        if not countBackground:
            rawProfile = imageProfile[1:].copy()
            imageProfile = imageProfile[1:]
        else:
            rawProfile = imageProfile.copy()
        imageProfile = imageProfile / np.sum(imageProfile)  # normalize the image profile
        return imageProfile, rawProfile  # , texture_features
    # end getImageProfile




# end class VoxelBase




if __name__ == '__main__':
    """Unit tests"""

    pass





# end main