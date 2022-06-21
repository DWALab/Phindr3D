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

import pandas
import os.path
from .DataFunctions import *
import numpy as np

try:
    from .Image import *
except ImportError:
    from Image import *

class Metadata:
    """This class handles groups of image files and the associated metadata.
       Static methods that draw closely from transliterations of the MATLAB functions
       can be found in the DataFunctions class."""

    def __init__(self):
        """Metadata class constructor"""

        # Set default values for member variables
        self.metadataLoadSuccess = False
        self.metadataFilename = ""
        self.images = {}


    # end constructor


    def SetMetadataFilename(self, omf):
        """Set method to check the type of the filename string
            and set the member variable. Returns True if successful,
            False on error."""
        if not isinstance(omf, str):
            return False
        else:
            self.metadataFilename = omf

    # end SetMetadataFilename

    def GetMetadataFilename(self):
        """Get method to return the metadata filename string."""

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
        """If there was a Treatment column in the metadata, Stack instances
            in stackLayers will have Treatment data. There should be a unique
            Treatment value for all stackLayers in an image, but if not, the
            Stack.GetTreatment method returns a list of the values found.
            This method chooses the first from the list, in such a case.
            This method creates a dictionary of imageIDs and the Treatment values,
            if they exist, or None if not. On error, returns an empty dictionary."""
        allTreatments = {}
        try:
            if len(self.images) > 0:
                for imgID in self.images:
                    tmpTreat = self.images[imgID].GetTreatment()
                    if isinstance(tmpTreat, str):
                        treat = tmpTreat
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
                    if isinstance(tmpTreat, str):
                        treatmentList.append(tmpTreat)
                    elif isinstance(tmpTreat, list):
                        treatmentList.extend(tmpTreat)
                # Use set to find unique values in a list, then change type back to list
                treatmentList = list(set(treatmentList))
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
            return idList
        except AttributeError:
            # Return an empty list
            return []
    # end GetAllImageIDs


    def computeImageParameters(self):
        """Call after loading metadata. Calls functions that compute the scaling factors and thresholds.
            On success, fills the scaling factor and intensity member variables and returns True.
            If the metadata did not load successfully, returns False
            On failure, returns False?
            """
        # If the metadata has not loaded successfully, return False
        if not self.metadataLoadSuccess:
            return False
        #


        return True
    # end computeImageParameters



    # This class should also include
    # rescale intensities
    # threshold images

    # class attributes
    # output metadata file name


# end class Metadata



if __name__ == '__main__':
    """Tests of the Metadata class that can be run directly."""
    # For testing purposes:
    # Running will prompt user for a text file, image id, stack id, and channel number
    # Since this is only for testing purposes, assume inputted values are all correct types

    metadatafile = input("Metadata file: ")
    imageid = float(input("Image ID: "))
    stackid = int(input("Stack ID: "))
    channelnumber = int(input("Channel Number: "))
    test = Metadata()
    if test.loadMetadataFile(metadatafile):
        print('Result:', test.images[imageid].layers[stackid].channels[channelnumber].channelpath)
        # using pandas, search through dataframe to find the correct element
        metadata = pandas.read_table(metadatafile, usecols=lambda c: not c.startswith('Unnamed:'), delimiter='\t')
        numrows = metadata.shape[0]
        for i in range(numrows):
            if (metadata.at[i, 'Stack'] == stackid) and (metadata.at[i, 'ImageID'] == imageid):
                print('Expect:', metadata.at[i, f'Channel_{channelnumber}'])
        print("So, did it load? " + "Yes!" if test.metadataLoadSuccess else "No.")
        print("===")
        print("Running computeImageParameters: " + "Successful" if test.computeImageParameters() else "Unsuccessful")
    else:
        print("loadMetadataFile was unsuccessful")

# end main
