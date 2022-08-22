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

#from mahotas.features import texture
import time
import imageio.v2 as io
import matplotlib.pyplot as plt

try:
    from .VoxelBase import *
    from .PixelImage import *
    from .SuperVoxelImage import *
    from .MegaVoxelImage import *
except ImportError:
    from src.VoxelGroups.VoxelBase import *
    from PixelImage import *
    from SuperVoxelImage import *
    from MegaVoxelImage import *

try:
    from ..PhindConfig.PhindConfig import *
    from ..Data.Metadata import *
except ImportError:
    from src.PhindConfig.PhindConfig import *
    from src.Data.Metadata import *


class VoxelGroups(VoxelBase):
    """From pixels to supervoxels to megavoxels"""

    def __init__(self, metaref):
        """Constructor"""
        self.metadata = metaref
        self.numVoxelBins = 20
        self.numSuperVoxelBins = 15
        self.numMegaVoxelBins = 40
        self.pixelImage = PixelImage()
        self.superVoxelImage = SuperVoxelImage()
        self.megaVoxelImage = MegaVoxelImage()


    # end constructor

    def action(self, outputFileName, training):
        """Action performed by this class when user requests the Phind operation.
            Returns the True/False result of the phindVoxelGroups method."""
        if self.phindVoxelGroups(training):
            if self.extractImageLevelTextureFeatures(outputFileName=outputFileName, training=training):
                return True
            else:
                return False
        else:
            return False

    # end action

    def phindVoxelGroups(self, training):
        """Phind operation.
            Returns True if successful, False on failure or error"""

        self.pixelImage.getPixelBinCenters(self.metadata, training)
        self.superVoxelImage.getSuperVoxelBinCenters(self.metadata, training, self.pixelImage)
        self.megaVoxelImage.getMegaVoxelBinCenters(self.metadata, training, self.pixelImage, self.superVoxelImage)

        print("Pixels:", self.pixelImage.pixelBinCenters)
        print("Super Voxels:", self.superVoxelImage.superVoxelBinCenters)
        print("Mega Voxels:", self.megaVoxelImage.megaVoxelBinCenters)

        return True
    # end phindVoxelGroups

    def extractImageLevelTextureFeatures(self, outputFileName='imagefeatures.csv', training=None):
        """Given pixel/super/megavoxel bin centers, creates a feature file"""
        #collect parameters from phindconfig
        countBackground = PhindConfig.countBackground
        textureFeatures = PhindConfig.textureFeatures
        treatmentCol = self.metadata.GetAllTreatments()
        numMegaVoxelBins = self.numMegaVoxelBins
        if countBackground:
            totalBins = numMegaVoxelBins + 1
        else:
            totalBins = numMegaVoxelBins
        #set up arrays to hold results
        uniqueImageID = self.metadata.GetAllImageIDs()
        tmpim = self.metadata.GetImage(uniqueImageID[0])
        tmpotherparams = tmpim.GetOtherParams()
        mdatavals = np.empty((len(uniqueImageID), len(tmpotherparams)), dtype='object')
        # for all images: put megavoxel frequencies
        resultIM = np.zeros((len(uniqueImageID), totalBins))
        resultRaw = np.zeros((len(uniqueImageID), totalBins))
        if textureFeatures:
            textureResults = np.zeros((len(uniqueImageID), 4))
        useTreatment = False
        if len(treatmentCol) > 0:
            useTreatment = True
            Treatments = []
        #timing things
        times = np.zeros(5)
        meantime = 0
        
        for iImages in range(len(uniqueImageID)):
            a = time.time()
            if iImages > 4 and iImages % 2 == 0:
                if np.mean(times) > meantime:
                    meantime = np.mean(times)
                estimate = f'Remaining time estimate ... {round(meantime * (len(uniqueImageID)-iImages)/60, 2)} minutes'
                print(estimate, end='\r')
            id = uniqueImageID[iImages]
            currentImage = self.metadata.GetImage(id)
            currentOtherParams = currentImage.GetOtherParams()
            for i, key in enumerate(list(currentOtherParams.keys())):
                mdatavals[iImages, i] = currentOtherParams[key]
            d = self.metadata.getImageInformation(currentImage, 0)
            # Pass in a new TileInfo object to provide default values
            theTileInfo = self.metadata.getTileInfo(d, TileInfo())
            pixelBinCenterDifferences = np.array([DataFunctions.mat_dot(self.pixelImage.pixelBinCenters, self.pixelImage.pixelBinCenters, axis=1)]).T
            superVoxelProfile, fgSuperVoxel = self.getTileProfiles(self.metadata, currentImage, self.pixelImage.pixelBinCenters, pixelBinCenterDifferences, theTileInfo)
            megaVoxelProfile, fgMegaVoxel, texture_features = self.getMegaVoxelProfile(self.superVoxelImage.superVoxelBinCenters, superVoxelProfile, theTileInfo, fgSuperVoxel, training, analysis=textureFeatures)
            imgProfile, rawProfile = self.getImageProfile(self.megaVoxelImage.megaVoxelBinCenters, megaVoxelProfile, theTileInfo, fgMegaVoxel)
            resultIM[iImages, :] = imgProfile
            resultRaw[iImages, :] = rawProfile
            if textureFeatures:
                textureResults[iImages, :] = texture_features
            if useTreatment:
                Treatments.append(currentImage.GetTreatment())
            b = time.time() - a
            times[iImages % 5] = b
        numRawMV = np.sum(resultRaw, axis=1)  # one value per image, gives number of megavoxels
        dictResults = {}
        for i, col in enumerate(list(currentOtherParams.keys())):
            dictResults[col] = mdatavals[:, i]
        if useTreatment:
            dictResults['Treatment'] = Treatments
        else:
            dictResults['Treatment'] = np.full((len(uniqueImageID),), 'RR', dtype='object')
        dictResults['NumMV'] = numRawMV
        for i in range(resultIM.shape[1]):
            mvlabel = f'MV{i + 1}'
            dictResults[mvlabel] = resultIM[:, i]  # e.g. mv cat 1: for each image, put here frequency of mvs of type 1.
        if textureFeatures:
            for i, name in enumerate(['text_ASM', 'text_entropy', 'text_info_corr1', 'text_infor_corr2']):
                dictResults[name] = textureResults[:, i]
        df = pd.DataFrame(dictResults)
        csv_name = outputFileName
        if csv_name[-4:] != '.txt':
            csv_name = csv_name + '.txt'
        df.to_csv(csv_name, index=None, sep='\t')
        print('\nAll done.')
        #return param, resultIM, resultRaw, df #, metaIndexTmp
        # Missing a first parameter from the return list
        return resultIM, resultRaw, df  # , metaIndexTmp
    # end extractImageLevelTextureFeatures



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

    #load metadata, compute parameters
    #phind bincenters in a deterministic manner + compare to expected result
    #compute phindr3D results on synthetic image set with the deterministic bincenters + compare to expected results.

    else:
        print("loadMetadataFile was unsuccessful")

# end main