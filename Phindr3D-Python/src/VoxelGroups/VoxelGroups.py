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
except ImportError:
    from src.PhindConfig.PhindConfig import *

import time

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
            theInfo = self.metadata.getTileInfo(d, TileInfo())


            superVoxelProfile, fgSuperVoxel \
                = self.getTileProfiles(tmpmdata, pixelBinCenters, theInfo)
            #    = getTileProfiles(tmpmdata, param.pixelBinCenters, param, analysis=True)





        # print('Writing data to file ...')
        # Output feature file to csv

        # ...

        # Final output from previous version
        #print('\nAll done.')
        #return param, resultIM, resultRaw, df #, metaIndexTmp
        print("Finished the extractImageLevelTextureFeatures method")
    # end extractImageLevelTextureFeatures


    def getTileProfiles(self, tmpmdata, pixelBinCenters, tileInfo):
        """Method that is a member of VoxelGroups that redirects
            to the VoxelFunctions getTileProfiles."""
        intensityNormPerTreatment = self.metadata.intensityNormPerTreatment
        return dfunc.getTileProfiles(tmpmdata, pixelBinCenters, tileInfo, intensityNormPerTreatment)
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