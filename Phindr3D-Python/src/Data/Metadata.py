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

try:
    from .Image import *
    from .DataFunctions import *
except ImportError:
    from Image import *
    from DataFunctions import *

try:
    from ..PhindConfig import *
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
        # self.intensityNormPerTreatment = False
        self.intensityNormPerTreatment = True
        self.randTrainingPerTreatment = 3

        # Set default values for internally-accessed member variables
        self.metadataLoadSuccess = False
        self.metadataFilename = ""
        self.images = {}

        # Training set, scale factors, and thresholds
        self.trainingSet = []
        self.scaleFactors = None
        self.thresholds = None
        self.lowerbound = [0, 0, 0]
        self.upperbound = [1, 1, 1]
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
                if os.path.exists(metadata.at[i, channel]) and (metadata.at[i, channel].endswith(".tiff") or metadata.at[i, channel].endswith(".tif")):
                    row.append(metadata.at[i, channel])
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
            something else if not."""
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

        if self.intensityNormPerTreatment:
            grpVal = np.zeros(numImages)
        # min values of all selected images in all channels
        minChannel = np.zeros((numImages, numChannels))
        # max values of all selected images in all channels
        maxChannel = np.zeros((numImages, numChannels))


    # end getScalingFactorforImages


    #   getScalingFactorforImages.m
    def getScalingFactorforImages(metadata, param):
        randFieldIDforNormalization = getTrainingFields(metadata, param)  # choose images for scaling
        if param.intensityNormPerTreatment:
            grpVal = np.zeros(randFieldIDforNormalization.size)
        minChannel = np.zeros(
            (randFieldIDforNormalization.size, param.numChannels))  # min values of all selected images in all channels
        maxChannel = np.zeros(
            (randFieldIDforNormalization.size, param.numChannels))  # max values of all selected images in all channels
        numImages = randFieldIDforNormalization.size
        for i in range(0, numImages):
            # which images
            id = randFieldIDforNormalization[i]  # which 3d image
            tmpmdata = metadata.loc[metadata[param.imageIDCol[0]] == id]
            zStack = np.ravel(tmpmdata[param.stackCol])
            depth = len(zStack)
            # used to be a getTileInfo here.
            randHalf = int(depth // 2)
            randZ = [zStack[j] for j in Generator.choice(depth, size=randHalf, replace=False,
                                                         shuffle=False)]  # choose half of the stack, randomly
            minVal = np.zeros((randHalf, param.numChannels))
            maxVal = np.zeros((randHalf, param.numChannels))
            for j in range(randHalf):
                for k in range(param.numChannels):
                    IM = io.imread(tmpmdata.loc[tmpmdata[param.stackCol[0]] == randZ[j], param.channelCol[k]].values[0])
                    minVal[j, k] = np.quantile(IM, 0.01)
                    maxVal[j, k] = np.quantile(IM, 0.99)
            minChannel[i, :] = np.amin(minVal, axis=0)
            maxChannel[i, :] = np.amax(maxVal, axis=0)
            if param.intensityNormPerTreatment:
                # index of the treatment for this image in the list of all treatment
                grpVal[i] = np.argwhere(param.allTreatments == tmpmdata[param.treatmentCol].values[
                    0])  # tmpdata[param.treatmentCol[0]][0] is the treatment of the current image

        if param.intensityNormPerTreatment:
            uGrp = np.unique(grpVal)
            param.lowerbound = np.zeros((uGrp.size, param.numChannels))
            param.upperbound = np.zeros((uGrp.size, param.numChannels))
            for i in range(0, uGrp.size):
                ii = grpVal == uGrp[i]
                if np.sum(ii) > 1:
                    param.lowerbound[i, :] = np.quantile(minChannel[grpVal == uGrp[i], :], 0.01)
                    param.upperbound[i, :] = np.quantile(maxChannel[grpVal == uGrp[i], :], 0.99)
                else:
                    param.lowerbound[i, :] = minChannel[grpVal == uGrp[i], :]
                    param.upperbound[i, :] = maxChannel[grpVal == uGrp[i], :]
        else:
            param.lowerbound = np.quantile(minChannel, 0.01, axis=0)
            param.upperbound = np.quantile(maxChannel, 0.99, axis=0)
        param.randFieldID = randFieldIDforNormalization  # added this here because I dont know where else this would be determined.
        return param





    def computeImageParameters(self):
        """Call after loading metadata. Calls functions that compute the scaling factors and thresholds.
            On success, fills the scaling factor and intensity member variables and returns True.
            If the metadata did not load successfully, returns False
            On failure, returns False?
            """
        # If the metadata has not loaded successfully, return False
        if not self.metadataLoadSuccess:
            return False
        # else

        theTrainingFields = self.getTrainingFields(PhindConfig.randTrainingFields)
        (lowerbound, upperbound) = self.getScalingFactorforImages(theTrainingFields)




        return True
    # end computeImageParameters

    # This class should also include
    # rescale intensities
    # threshold images


# end class Metadata

if __name__ == '__main__':
    """Tests of the Metadata class that can be run directly."""
    # For testing purposes:
    # Running will prompt user for a text file, image id, stack id, and channel number
    # Since this is only for testing purposes, assume inputted values are all correct types

    # metadatafile = r"R:\\Phindr3D-Dataset\\neurondata\\Phindr3D_neuron-sample-data\\metaout_metadatafile.txt"
    #metadatafile = r"R:\\Phindr3D-Dataset\\Phindr3D_TreatmentID_sample_data\\mike_test.txt"
    metadatafile = r"C:\\mschumaker\\projects\\Phindr3D\\Phindr3D-Python\\testdata\\metadata_tests\\set1_treatments\\mike_test.txt"


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

    #finalOut = test.getTrainingFields(PhindConfig.randTrainingFields)
    #print("final getTrainingFields output")
    #print(finalOut)

    finalOut = test.computeImageParameters()


# end main
