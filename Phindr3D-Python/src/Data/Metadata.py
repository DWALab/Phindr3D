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

# Static functions for data and metadata handling
import numpy as np
import pandas
import os.path
import imageio.v2 as io
import imagecodecs

try:
    from .Image import *
    from .DataFunctions import *
except ImportError:
    from Image import *
    from DataFunctions import *

try:
    from ..PhindConfig.PhindConfig import *
except ImportError:
    from src.PhindConfig.PhindConfig import *

# Initialize a random number generator
Generator = np.random.default_rng()

class Metadata:
    """This class handles groups of image files and the associated metadata.
       Static methods that draw closely from transliterations of the MATLAB functions
       can be found in the DataFunctions class."""

    def __init__(self):
        """Metadata class constructor"""
        # Define user-controlled parameters and set default values
        self.intensityNormPerTreatment = False
        self.randTrainingPerTreatment = 1

        # Set default values for internally-accessed member variables
        self.metadataLoadSuccess = False
        self.metadataFilename = ""
        self.images = {}

        # Training set, scale factors, and thresholds
        self.trainingSet = []
        self.scaleFactors = None
        self.intensityThresholdValues = None
        self.intensityThreshold = None
        self.lowerbound = [0, 0, 0]
        self.upperbound = [1, 1, 1]

        # Tile configuration and info from getTileInfo
        self.theTileInfo = TileInfo()

    # end constructor


    def SetMetadataFilename(self, omf):
        """Set method to check the type of the filename string
            and set the member variable. Returns True if successful,
            False on error."""
        if not isinstance(omf, str):
            return False
        else:
            self.metadataFilename = omf
            return True
    # end SetMetadataFilename

    def GetMetadataFilename(self):
        """Get method to return the metadata filename string.
            If the filename is empty or None, return False"""
        if self.metadataFilename is None:
            return False
        elif self.metadataFilename == "":
            return False
        else:
            return self.metadataFilename
    # end GetMetadataFilename

    def metadataFileExists(self, omf):
        """Check whether the filename specified already exists.
            Returns True if the file exists, False if it does not, or if the given
            argument is not a string."""
        if not isinstance(omf, str):
            return False
        else:
            return os.path.exists(omf)
    # end metadataFileExists

    def loadMetadataFile(self, filepath):
        # Loads metadata file into a hierarchy of classes
        # Returns true if successful, prints error message and returns false if failure
        if not self.metadataFileExists(filepath):
            raise FileNotFoundError
        metadata = pandas.read_table(filepath, usecols=lambda c: not c.startswith('Unnamed:'), delimiter='\t')
        numrows = metadata.shape[0]
        rows = []
        # counts channels
        channels = []
        for col in metadata:
            if col.startswith('Channel_'):
                channels.append(col)
        # if there are no channels, stack, or imageid, return error
        if channels == [] or ('Stack' not in metadata) or ('ImageID' not in metadata):
            raise MissingChannelStackError

        # takes input metadata and stores in a list of tuples, each representing a row of metadata
        for i in range(numrows):
            row = []
            for channel in channels:
                if os.path.exists(metadata.at[i, channel]) \
                    and (metadata.at[i, channel].endswith(".tiff")
                         or metadata.at[i, channel].endswith(".tif")):
                    row.append(metadata.at[i, channel])
                #if os.path.exists(metadata[channel].str.replace(r'\\', '/', regex=True)[i]) and (metadata.at[i, channel].endswith(".tiff") or metadata.at[i, channel].endswith(".tif")):
                #    row.append(metadata[channel].str.replace(r'\\', '/', regex=True)[i])
                else:
                    raise MissingChannelStackError
            # add additional parameter columnlabels, except for channels, stack, metadatafile, and image id
            # these will be ordered at the end, for referencing purposes
            # order of a row of data: Channels, Other Parameters, Stack, MetadataFile, ImageID
            for col in metadata:
                if col.startswith('Channel_') or col == 'Stack' or col == 'MetadataFile' or col == 'ImageID':
                    continue
                row.append(metadata.at[i, col])
            row.append(metadata.at[i, 'Stack'])
            row.append(metadata.at[i, 'MetadataFile'])
            row.append(metadata.at[i, 'ImageID'])
            rows.append(row)

        # to make storing data in the other image classes easier, create list of column names
        # each column's index refers to what data is stored in that index of a row
        columnlabels = []
        for chan in channels:
            columnlabels.append(chan)
        for col in metadata:
            if col.startswith('Channel_') or col == 'Stack' or col == 'MetadataFile' or col == 'ImageID':
                continue
            columnlabels.append(col)
        columnlabels.append('Stack')
        columnlabels.append('MetadataFile')
        columnlabels.append('ImageID')

        # puts each row into a dictionary, sorted by image ids
        rowdict = {}
        for row in rows:
            imageid = row[row.__len__() - 1]
            if imageid in rowdict:
                rowdict[imageid].append(row)
            else:
                rowdict[imageid] = []
                rowdict[imageid].append(row)

        # create list of Images
        imageSet = {}
        for imageID in rowdict:
            anImage = Image()
            anImage.setImageID(imageID)
            anImage.addStackLayers(rowdict[imageID], columnlabels)
            imageSet[imageID] = anImage
        self.images = imageSet
        self.SetMetadataFilename(filepath)

        # Set an internal parameter to indicate that metadata has loaded successfully
        self.metadataLoadSuccess = True
        return True
    # end loadMetadataFile

    def GetNumChannels(self):
        try:
            for image in self.images:
                for stack in self.images[image].stackLayers:
                    # This will return after the first stack in the first image
                    return len(self.images[image].stackLayers[stack].channels)
        except AttributeError:
            # If any of the members can't be found, AttributeError will be raised
            return 0
        # if there are no images or no stacks, there are no channels
        return 0
    # end GetNumChannels

    def GetAllTreatments(self):
        """If there was a Treatment column in the metadata, Image instances
            in images will have Treatment data. The Image.GetTreatment method
            returns a list of the treatment values found in that Image.
            This method chooses the first from the list.
            This method creates a dictionary of imageIDs and the Treatment values,
            if they exist, or None if not. On error, returns an empty dictionary."""
        allTreatments = {}
        try:
            if len(self.images) > 0:
                for imgID in self.images:
                    tmpTreat = self.images[imgID].GetTreatment()
                    if tmpTreat is None:
                        treat = None
                    elif isinstance(tmpTreat, list):
                        treat = tmpTreat[0]
                    else:
                        treat = None
                    allTreatments[imgID] = treat
            else:
                pass
            return allTreatments
        except AttributeError:
            # Return an empty dictionary
            return {}
    # end GetAllTreatments

    def GetTreatmentTypes(self):
        """If there was a Treatment column in the metadata, Stack instances
            in stackLayers will have Treatment data. There should be a unique
            Treatment value for all stackLayers in an image, but if not, the
            Stack.GetTreatment method returns a list of the values found.
            This method collects the treatment types, including multiple treatments
            in the same image, if this condition exists.
            This method returns a list of strings of all treatment types if they
            exist, or an empty string if not. Returns an empty string on error. """
        treatmentList = []
        try:
            if len(self.images) > 0:
                for imgID in self.images:
                    tmpTreat = self.images[imgID].GetTreatment()
                    if isinstance(tmpTreat, list):
                        treatmentList.extend(tmpTreat)
                    else:
                        pass
                # Use set to find unique values in a list, then change type back to list
                treatmentList = list(set(treatmentList))
                treatmentList.sort()
            else:
                pass
            return treatmentList
        except AttributeError:
            # Return an empty list
            return []
    # end GetTreatmentTypes

    def GetAllImageIDs(self):
        """Returns a list of all the image ID values, if found.
            If no image IDs are found, an empty list is returned."""
        idList = []
        try:
            if len(self.images) > 0:
                for imgID in self.images:
                    idList.append(imgID)
            else:
                pass
            # Use set to find unique values, then change type back to list
            idList = list(set(idList))
            idList.sort()
            return idList
        except AttributeError:
            # Return an empty list
            return []
    # end GetAllImageIDs

    def GetImage(self, theImageID):
        """Returns the Image class with the given image ID, if it is found.
            If the requested image ID is not found, returns None."""
        # Attempt to get the Image object with the given ID, return None on failure
        try:
            return self.images[theImageID]
        except (IndexError, AttributeError, KeyError):
            return None
    # end GetImage

    def getTrainingFields(self, numTrainingFields=10):
        """
        Get smaller subset of images (usually 10) to define parameters for further analysis.
        (nly used for scaling factors to scale down intensities from 0 to 1).
        output is a Numpy array of a subset of image IDs.
        On error, returns an empty numpy array
        """
        randFieldID = np.array([])

        # Check the type of numTrainingFields
        if not isinstance(numTrainingFields, int):
            return randFieldID

        # Get the list of all image IDs in the set
        uniqueImageID = np.array(self.GetAllImageIDs())
        numImageIDs = len(uniqueImageID)

        # randTrainingFields is numTrainingFields, unless numTrainingFields is larger than numImageIDs
        randTrainingFields = numImageIDs if numImageIDs < numTrainingFields else numTrainingFields

        if not self.intensityNormPerTreatment:
            randFieldID = np.array([uniqueImageID[i] for i in
                Generator.choice(uniqueImageID.size, size=randTrainingFields,
                    replace=False, shuffle=False)])
        else:
            # have different treatments, want to choose training images from each treatment.
            uTreat = self.GetTreatmentTypes()
            allTreatments = self.GetAllTreatments()
            allTrKeys = np.array(list(allTreatments.keys()))
            allTrValues = np.array(list(allTreatments.values()))
            randTrainingPerTreatment = \
                -(-randTrainingFields//len(uTreat)) #ceiling division
            randFieldIDList = []
            for treat in uTreat:
                tempList = []
                try:
                    treatmentIDs = allTrKeys[allTrValues == treat]
                    if len(treatmentIDs) > 0:
                        tempList = [treatmentIDs[j] for j in
                            Generator.choice(len(treatmentIDs), size=randTrainingPerTreatment,
                                replace=False, shuffle=False)]
                except (ValueError,KeyError):
                    tempList = []
                randFieldIDList = randFieldIDList + tempList
            randFieldIDList.sort()
            randFieldID = np.array(randFieldIDList)
        #end if
        # output is randFieldID is a Numpy array of image ids
        return randFieldID
    # end getTrainingFields

    def getScalingFactorforImages(self, randFieldIDforNormalization):
        """compute lower and higher scaling values for each image"""
        # randFieldIDforNormalization is the IDs of the images for training
        # On error, return the following value
        errorVal = ([0,0,0], [1,1,1])
        if randFieldIDforNormalization.size == 0:
            return errorVal
        # else
        numChannels = self.GetNumChannels()
        numImages = randFieldIDforNormalization.size
        # Get the list of all treatment types
        allTreatmentTypes = self.GetTreatmentTypes()

        if self.intensityNormPerTreatment:
            grpVal = np.zeros(numImages)
        # blank array for min values of all selected images in all channels
        minChannel = np.zeros((numImages, numChannels))
        # blank array for max values of all selected images in all channels
        maxChannel = np.zeros((numImages, numChannels))

        for i in range(0, numImages):
            # which images
            theID = int(randFieldIDforNormalization[i])  # which 3d image
            theImageObject = self.GetImage(theID)
            zStack = theImageObject.stackLayers # dictionary
            # Get the number of stack layers in the image
            depth = len(zStack)
            zStackKeys = list(zStack.keys())
            randHalf = int(depth // 2)
            # choose half of the stack, randomly
            generatedArray = Generator.choice(depth, size=randHalf, replace=False, shuffle=False)
            # TO DO Add try-catch here for KeyError
            randZ = [zStackKeys[int(j)] for j in generatedArray]
            minVal = np.zeros((randHalf, numChannels))
            maxVal = np.zeros((randHalf, numChannels))

            for j in range(len(randZ)):
                theStackObject = zStack[randZ[j]]
                theChannels = theStackObject.channels
                channelKeys = list(theChannels.keys())
                for k in range(len(channelKeys)):
                    # TO DO Add try-catch here for KeyError
                    imFilePath = theChannels[channelKeys[k]].channelpath
                    # TO DO Add try-catch here for IOError (or similar - check imread api)
                    IM = io.imread(imFilePath)
                    minVal[j, k] = np.quantile(IM, 0.01)
                    maxVal[j, k] = np.quantile(IM, 0.99)
            minChannel[i, :] = np.amin(minVal, axis=0)
            maxChannel[i, :] = np.amax(maxVal, axis=0)

            if self.intensityNormPerTreatment:
                # index of the treatment for this image in the list of all treatments
                # if the treatment type is not found (or there are no treatments), return error
                try:
                    grpVal[i] = allTreatmentTypes.index(theImageObject.GetTreatment()[0])
                except (ValueError, IndexError):
                    return errorVal
        # end for images

        if self.intensityNormPerTreatment:
            uGrp = np.unique(grpVal)
            lowerbound = np.zeros((uGrp.size, numChannels))
            upperbound = np.zeros((uGrp.size, numChannels))
            for i in range(0, uGrp.size):
                ii = grpVal == uGrp[i]
                if np.sum(ii) > 1:
                    lowerbound[i, :] = np.quantile(minChannel[grpVal == uGrp[i], :], 0.01)
                    upperbound[i, :] = np.quantile(maxChannel[grpVal == uGrp[i], :], 0.99)
                else:
                    lowerbound[i, :] = minChannel[grpVal == uGrp[i], :]
                    upperbound[i, :] = maxChannel[grpVal == uGrp[i], :]
        else:
            lowerbound = np.quantile(minChannel, 0.01, axis=0)
            upperbound = np.quantile(maxChannel, 0.99, axis=0)
        return (lowerbound, upperbound)
    # end getScalingFactorforImages

    def getImageInformation(self, theImage):
        """Get information about the image files.
            Called in getPixelBinCenters, getImageThresholdValues,
            extractImageLevelTextureFeatures"""
        d = np.ones(3, dtype=int)
        # Get one file name from the full 3D image
        # (first file is convenient.)
        try:
            d[2] = len(theImage.stackLayers)
        except AttributeError:
            d[2] = 0
        try:
            # dictionaries are ordered as of Python 3.7,
            # but we will not assume what version of Python 3 is being used
            firstStack = theImage.stackLayers[list(theImage.stackLayers.keys())[0]]
            firstChannel = firstStack.channels[list(firstStack.channels.keys())[0]]
            imFileName = firstChannel.channelpath
            # imfinfo is matlab built-in,
            # so replicate its action in DataFunctions
            info = DataFunctions.imfinfo(imFileName)
            d[0] = info.Height
            d[1] = info.Width
        except (IndexError, AttributeError):
            d[0] = 0
            d[1] = 1
        return d
    # end getImageInformation

    def getTileInfo(self, dimSize, tileInfo):
        """computes how many pixels and stacks that need to be retained based on user choices.
            Called in getPixelBinCenters, extractImageLevelTextureFeatures,
            getImageThresholdValues, getSuperVoxelbinCenters.
            This method gets configuration information from PhindConfig"""
        xOffset = dimSize[0] % tileInfo.tileX
        yOffset = dimSize[1] % tileInfo.tileY
        zOffset = dimSize[2] % tileInfo.tileZ

        if xOffset % 2 == 0:
            tileInfo.xOffsetStart = int(xOffset / 2 + 1) - 1  # remember 0 indexing in python
            tileInfo.xOffsetEnd = int(xOffset / 2)
        else:
            tileInfo.xOffsetStart = int(xOffset // 2 + 1) - 1
            tileInfo.xOffsetEnd = int(-(-xOffset // 2))  # ceiling division is the same as upside-down floor division.
        if yOffset % 2 == 0:
            tileInfo.yOffsetStart = int(yOffset / 2 + 1) - 1
            tileInfo.yOffsetEnd = int(yOffset / 2)
        else:
            tileInfo.yOffsetStart = int(yOffset // 2 + 1) - 1
            tileInfo.yOffsetEnd = int(-(-yOffset // 2))
        if zOffset % 2 == 0:
            tileInfo.zOffsetStart = int(zOffset / 2 + 1) - 1
            tileInfo.zOffsetEnd = int(zOffset / 2)
        else:
            tileInfo.zOffsetStart = int(zOffset // 2 + 1) - 1
            tileInfo.zOffsetEnd = int(-(-zOffset // 2))

        tileInfo.croppedX = dimSize[0] - tileInfo.xOffsetStart - tileInfo.xOffsetEnd
        tileInfo.croppedY = dimSize[1] - tileInfo.yOffsetStart - tileInfo.yOffsetEnd
        tileInfo.croppedZ = dimSize[2] - tileInfo.zOffsetStart - tileInfo.zOffsetEnd

        superVoxelXOffset = (tileInfo.croppedX / tileInfo.tileX) % tileInfo.megaVoxelTileX
        superVoxelYOffset = (tileInfo.croppedY / tileInfo.tileY) % tileInfo.megaVoxelTileY
        superVoxelZOffset = (tileInfo.croppedZ / tileInfo.tileZ) % tileInfo.megaVoxelTileZ
        tileInfo.origX = dimSize[0]
        tileInfo.origY = dimSize[1]
        tileInfo.origZ = dimSize[2]

        if superVoxelXOffset % 2 == 0:
            tileInfo.superVoxelXOffsetStart = superVoxelXOffset / 2 + 1
            tileInfo.superVoxelXOffsetEnd = superVoxelXOffset / 2
        else:
            tileInfo.superVoxelXOffsetStart = superVoxelXOffset // 2 + 1
            tileInfo.superVoxelXOffsetEnd = -(-superVoxelXOffset // 2)  # same floor division trick.
        if superVoxelXOffset != 0:  # add pixel rows if size of supervoxels are not directly visible
            numSuperVoxelsToAddX = tileInfo.megaVoxelTileX - superVoxelXOffset
            if numSuperVoxelsToAddX % 2 == 0:
                tileInfo.superVoxelXAddStart = int(numSuperVoxelsToAddX / 2)
                tileInfo.superVoxelXAddEnd = int(numSuperVoxelsToAddX / 2)
            else:
                tileInfo.superVoxelXAddStart = int(numSuperVoxelsToAddX // 2)
                tileInfo.superVoxelXAddEnd = int(-(-numSuperVoxelsToAddX // 2))
        else:
            tileInfo.superVoxelXAddStart = int(0)
            tileInfo.superVoxelXAddEnd = int(0)

        # same along other axes.
        if superVoxelYOffset != 0:
            numSuperVoxelsToAddY = tileInfo.megaVoxelTileY - superVoxelYOffset
            if numSuperVoxelsToAddY % 2 == 0:
                tileInfo.superVoxelYAddStart = int(numSuperVoxelsToAddY / 2)
                tileInfo.superVoxelYAddEnd = int(numSuperVoxelsToAddY / 2)
            else:
                tileInfo.superVoxelYAddStart = int(numSuperVoxelsToAddY // 2)
                tileInfo.superVoxelYAddEnd = int(-(- numSuperVoxelsToAddY // 2))
        else:
            tileInfo.superVoxelYAddStart = int(0)
            tileInfo.superVoxelYAddEnd = int(0)
        if superVoxelZOffset != 0:
            numSuperVoxelsToAddZ = tileInfo.megaVoxelTileZ - superVoxelZOffset
            if numSuperVoxelsToAddZ % 2 == 0:
                tileInfo.superVoxelZAddStart = int(numSuperVoxelsToAddZ / 2)
                tileInfo.superVoxelZAddEnd = int(numSuperVoxelsToAddZ / 2)
            else:
                tileInfo.superVoxelZAddStart = int(numSuperVoxelsToAddZ // 2)
                tileInfo.superVoxelZAddEnd = int(-(-numSuperVoxelsToAddZ // 2))
        else:
            tileInfo.superVoxelZAddStart = int(0)
            tileInfo.superVoxelZAddEnd = int(0)
        # continue first part of supervoxels offset parity with other axes
        if superVoxelYOffset % 2 == 0:
            tileInfo.superVoxelYOffsetStart = int(superVoxelYOffset / 2 + 1) - 1
            tileInfo.superVoxelYOffsetEnd = int(superVoxelYOffset / 2)
        else:
            tileInfo.superVoxelYOffsetStart = int(superVoxelYOffset // 2 + 1) - 1
            tileInfo.superVoxelYOffsetEnd = int(-(-superVoxelYOffset // 2))
        if superVoxelZOffset % 2 == 0:
            tileInfo.superVoxelZOffsetStart = int(superVoxelZOffset / 2 + 1) - 1
            tileInfo.superVoxelZOffsetEnd = superVoxelZOffset / 2
        else:
            tileInfo.superVoxelZOffsetStart = int(superVoxelZOffset // 2 + 1) - 1
            tileInfo.superVoxelZOffsetEnd = int(-(-superVoxelZOffset // 2))

        tileInfo.numSuperVoxels = (tileInfo.croppedX * tileInfo.croppedY * tileInfo.croppedZ) // (
                    tileInfo.tileX * tileInfo.tileY * tileInfo.tileZ)  # supposed to be all elementwise operations (floor division too)
        tileInfo.numSuperVoxelsXY = (tileInfo.croppedX * tileInfo.croppedY) / (tileInfo.tileX * tileInfo.tileY)

        tmpX = (tileInfo.croppedX / tileInfo.tileX) + superVoxelXOffset
        tmpY = (tileInfo.croppedY / tileInfo.tileY) + superVoxelYOffset
        tmpZ = (tileInfo.croppedZ / tileInfo.tileZ) + superVoxelZOffset

        tileInfo.numMegaVoxels = int(
            (tmpX * tmpY * tmpZ) // (tileInfo.megaVoxelTileX * tileInfo.megaVoxelTileY * tileInfo.megaVoxelTileZ))
        tileInfo.numMegaVoxelsXY = int((tmpX * tmpY) / (tileInfo.megaVoxelTileX * tileInfo.megaVoxelTileY))
        return tileInfo
    # end getTileInfo

    def getIndividualChannelThreshold(self, theImage, theTileInfo):
        """individual channel threshold"""
        numChannels = self.GetNumChannels()
        allTreatmentTypes = self.GetTreatmentTypes()
        errorVal = np.zeros((len(theImage.stackLayers), numChannels))
        thresh = np.zeros((len(theImage.stackLayers), numChannels))

        if self.intensityNormPerTreatment:
            # index of the treatment for this image in the list of all treatments
            # if the treatment type is not found (or there are no treatments), return error
            try:
                grpVal = allTreatmentTypes.index(theImage.GetTreatment()[0])
            except (ValueError, IndexError):
                return errorVal
        # end if
        for iImages in range(len(theImage.stackLayers)):
            for iChannels in range(numChannels):
                try:
                    stackIndex = list(theImage.stackLayers.keys())[iImages]
                    theStack = theImage.stackLayers[stackIndex]
                    channelIndex = list(theStack.channels.keys())[iChannels]
                    theChannel = theStack.channels[channelIndex]
                    imFileName = theChannel.channelpath
                except (IndexError, AttributeError):
                    return errorVal
                IM = io.imread(imFileName)
                xEnd = -theTileInfo.xOffsetEnd
                if xEnd == -0:
                    # if the end index is -0, you just index from 1 to behind 1
                    # and get an empty array. change to 0 if the dimOffsetEnd value is 0.
                    xEnd = None
                yEnd = -theTileInfo.yOffsetEnd
                if yEnd == -0:
                    yEnd = None
                IM = IM[theTileInfo.xOffsetStart:xEnd, theTileInfo.yOffsetStart:yEnd]

                if self.intensityNormPerTreatment:
                    IM = DataFunctions.rescaleIntensity(IM,
                        low=self.lowerbound[grpVal, iChannels], high=self.upperbound[grpVal, iChannels])
                else:
                    IM = DataFunctions.rescaleIntensity(IM,
                        low=self.lowerbound[iChannels], high=self.upperbound[iChannels])
                # want double precision here. not sure if python can handle this since
                # rounding error occurs at 1e-16, but will make float64 anyway
                thresh[iImages, iChannels] = DataFunctions.getImageThreshold(IM.astype('float64'))
        return thresh
    # end getIndividualChannelThreshold

    def getImageThresholdValues(self, randFieldID):
        """get image threshold values for dataset.
            On error return one row of num channels entries, each entry np.nan
            """
        numChannels = self.GetNumChannels()
        intensityThresholdValues = np.full((5000, numChannels), np.nan)  # not sure why we want 5000 rows
        # define a value to return on error
        errorVal = np.full((1, numChannels), np.nan)
        startVal = 0
        endVal = 0

        # for each of the randomly selected images chosen in
        for id in randFieldID:
            theImageObject = self.GetImage(id)
            d = self.getImageInformation(theImageObject)
            self.theTileInfo = self.getTileInfo(d, self.theTileInfo)
            tempThreshold = self.getIndividualChannelThreshold(theImageObject, self.theTileInfo)
            intensityThresholdValues[startVal:endVal+tempThreshold.shape[0], :] = tempThreshold
            startVal += tempThreshold.shape[0]
            endVal += tempThreshold.shape[0]
        # remember everything gets rescaled from 0 to 1 #drop rows containing nan,
        # then take medians for each channel#intensityThresholdValues[ii]
        outputThresholdValues = \
            intensityThresholdValues[np.isfinite(intensityThresholdValues).any(axis=1)]

        # remember everything gets rescaled from 0 to 1
        # drop rows containing nan, then take medians for each channel#intensityThresholdValues[ii]
        return outputThresholdValues
    # end getImageThresholdValues

    def computeImageParameters(self):
        """Call after loading metadata. Calls functions that compute the scaling factors and thresholds.
            On success, fills the scaling factor and intensity member variables and returns True.
            If the metadata did not load successfully, returns False
            """
        # If the metadata has not loaded successfully, return False
        if not self.metadataLoadSuccess:
            return False
        # else
        # TO DO: catch errors, return False if caught
        theTrainingFields = self.getTrainingFields(PhindConfig.randTrainingFields)
        (self.lowerbound, self.upperbound) = self.getScalingFactorforImages(theTrainingFields)
        self.intensityThresholdValues = self.getImageThresholdValues(theTrainingFields)

        intensityThreshold = np.quantile(self.intensityThresholdValues,
            PhindConfig.intensityThresholdTuningFactor, axis=0)
        self.intensityThreshold = np.reshape(intensityThreshold, (1, self.GetNumChannels()))
        return True
    # end computeImageParameters

# end class Metadata

if __name__ == '__main__':
    """Tests of the Metadata class that can be run directly."""
    # For testing purposes:
    # Running will prompt user for a text file, image id, stack id, and channel number
    # Since this is only for testing purposes, assume inputted values are all correct types

    metadatafile = r"R:\\Phindr3D-Dataset\\neurondata\\Phindr3D_neuron-sample-data\\builder_test.txt"
    #metadatafile = r"R:\\Phindr3D-Dataset\\Phindr3D_TreatmentID_sample_data\\mike_test.txt"
    #metadatafile = r"C:\\mschumaker\\projects\\Phindr3D\\Phindr3D-Python\\testdata\\metadata_tests\\set1_treatments\\mike_test.txt"


    # metadatafile = input("Metadata file: ")
    # imageid = float(input("Image ID: "))
    # stackid = int(input("Stack ID: "))
    # channelnumber = int(input("Channel Number: "))
    test = Metadata()
    if test.loadMetadataFile(metadatafile):
        # print('Result:', test.images[imageid].layers[stackid].channels[channelnumber].channelpath)
        # using pandas, search through dataframe to find the correct element
        # metadata = pandas.read_table(metadatafile, usecols=lambda c: not c.startswith('Unnamed:'), delimiter='\t')
        # numrows = metadata.shape[0]
        # for i in range(numrows):
        #    if (metadata.at[i, 'Stack'] == stackid) and (metadata.at[i, 'ImageID'] == imageid):
        #        print('Expect:', metadata.at[i, f'Channel_{channelnumber}'])
        print("So, did it load? " + "Yes!" if test.metadataLoadSuccess else "No.")
        print("===")
        print("Running computeImageParameters: " + "Successful" if test.computeImageParameters() else "Unsuccessful")
    else:
        print("loadMetadataFile was unsuccessful")
# end main
