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

try:
    from .VoxelBase import *
    from .PixelImage import *
    from .SuperVoxelImage import *
    from .MegaVoxelImage import *
except ImportError:
    from VoxelBase import *
    from PixelImage import *
    from SuperVoxelImage import *
    from MegaVoxelImage import *

try:
    from ..PhindConfig.PhindConfig import *
    from ..Data.Metadata import *
except ImportError:
    from src.PhindConfig.PhindConfig import *
    from src.Data.Metadata import *

import time
import imageio.v2 as io
import matplotlib.pyplot as plt

class VoxelGroups:
    """From pixels to supervoxels to megavoxels"""

    def __init__(self, metaref):
        """Constructor"""
        self.metadata = metaref
        self.numVoxelBins = 20
        self.numSuperVoxelBins = 15
        self.numMegaVoxelBins = 40

    # end constructor


    def action(self):
        """Action performed by this class when user requests the Phind operation.
            Returns the True/False result of the phindVoxelGroups method."""
        return self.phindVoxelGroups()
    # end action


    def phindVoxelGroups(self):
        """Phind operation.
            Returns True if successful, False on failure or error"""
        print("Entered the phindVoxelGroups method")
        # Steps (MATLAB)
        # param = getPixelBinCenters(mData, allImageId, param);
        # param = getSuperVoxelBinCenters(mData, allImageId, param);
        # param = getMegaVoxelBinCenters(mData, allImageId, param);

        # Then...
        # In MATLAB
        # extractImageLevelTextureFeatures(mData,allImageId,param,outputFileName,outputDir);
        # In Python
        # param, resultIM, resultRaw, df
        # = phi.extractImageLevelTextureFeatures(mdata, param, outputFileName=output_file_name, outputDir='')
        # This is the step that outputs a feature file

        pixelBinCenters = 1

        self.extractImageLevelTextureFeatures()



        print("Finished the phindVoxelGroups method")
        # temporary
        return True
    # end phindVoxelGroups


    def extractImageLevelTextureFeatures(self,
        outputFileName='imagefeatures.csv', outputDir=''):
        """Given pixel/super/megavoxel bin centers, creates a feature file"""
        print("Entered the extractImageLevelTextureFeatures method")

        countBackground = PhindConfig.countBackground
        textureFeatures = PhindConfig.textureFeatures
        treatmentCol = self.metadata.GetAllTreatments()
        numVoxelBins = self.numVoxelBins
        numSuperVoxelBins = self.numSuperVoxelBins
        numMegaVoxelBins = self.numMegaVoxelBins

        # Previously calculated - dummy type for now
        pixelBinCenters = np.zeros((200,3))
        #outputFileName
        #outputDir

        if countBackground:
            totalBins = numMegaVoxelBins + 1
        else:
            totalBins = numMegaVoxelBins
        uniqueImageID = self.metadata.GetAllImageIDs()
        # for all images: put megavoxel frequencies
        resultIM = np.zeros((len(uniqueImageID), totalBins))
        resultRaw = np.zeros((len(uniqueImageID), totalBins))
        if textureFeatures:
            textureResults = np.zeros((len(uniqueImageID), 4))
        useTreatment = False
        if len(treatmentCol) > 0:
            useTreatment = True
            Treatments = []
        timeupdates = len(uniqueImageID)//5

        # default value for timeperimage
        timeperimage = 0
        for iImages in range(len(uniqueImageID)):
            if (iImages == 1) or ((iImages > 3) and ((iImages + 1) % timeupdates == 0)):
                print(
                    f'Remaining time estimate ... {round(timeperimage * (len(uniqueImageID) - iImages) / 60, 2)} minutes')
            if iImages == 0:
                a = time.time()
            id = uniqueImageID[iImages]
            tmpmdata = self.metadata.GetImage(id)
            d = self.metadata.getImageInformation(tmpmdata, 0)
            # Pass in a new TileInfo object to provide default values
            theTileInfo = self.metadata.getTileInfo(d, TileInfo())

            pixelBinCenterDifferences = 1
            superVoxelProfile, fgSuperVoxel = \
            self.getTileProfiles(tmpmdata, pixelBinCenters, pixelBinCenterDifferences, theTileInfo)


        # print('Writing data to file ...')
        # Output feature file to csv

        # ...

        # Final output from previous version
        #print('\nAll done.')
        #return param, resultIM, resultRaw, df #, metaIndexTmp
        print("Finished the extractImageLevelTextureFeatures method")
    # end extractImageLevelTextureFeatures


    def getTileProfiles(self, imageObject, pixelBinCenters, pixelBinCenterDifferences, theTileInfo):
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
        allTreatmentTypes = self.metadata.GetTreatmentTypes()
        intensityNormPerTreatment = self.metadata.intensityNormPerTreatment
        intensityThreshold = self.metadata.intensityThreshold
        lowerbound = self.metadata.lowerbound
        upperbound = self.metadata.upperbound
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
        print(tmpData)
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
            pixelCategory = np.argmin(np.add(pixelBinCenterDifferences,
                dfunc.mat_dot(x[fg,:], x[fg,:], axis=1)).T - 2*(x[fg,:] @ pixelBinCenters.T), axis=1) + 1
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



# end class VoxelGroups




if __name__ == '__main__':
    """Unit testing"""
    from src.Data.Metadata import *
    metadatafile = r"R:\\Phindr3D-Dataset\\neurondata\\Phindr3D_neuron-sample-data\\builder_test.txt"

    test = Metadata()
    if test.loadMetadataFile(metadatafile):
        print("So, did the metadata load? " + "Yes!" if test.metadataLoadSuccess else "No.")
        print("===")
        print("Running computeImageParameters: " + "Successful" if test.computeImageParameters() else "Unsuccessful")
        print("===")

        print("Phind voxel action")
        vox = VoxelGroups(test)
        vox.action()

    else:
        print("loadMetadataFile was unsuccessful")

# end main