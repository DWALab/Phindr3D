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
    from .VoxelFunctions import *
except ImportError:
    from VoxelFunctions import *

try:
    from ..PhindConfig.PhindConfig import *
except ImportError:
    from src.PhindConfig.PhindConfig import *

import matplotlib.pyplot as plt
from mahotas.features import texture
import mahotas as mt

class VoxelBase:
    """From pixels to supervoxels to megavoxels"""

    def __init__(self):
        """Constructor"""
        self.numVoxelBins = PhindConfig.numVoxelBins
        self.numMegaVoxelBins = PhindConfig.numMegaVoxelBins
        self.textureFeatures = PhindConfig.textureFeatures
        # This is confusing and hopefully we can change it
        self.texture_features = False

    def getPixelBins(self, x, metadata, numBins):
        """Base class redirect to the static method in the VoxelFunctions class"""
        return VoxelFunctions.getPixelBins(x, metadata, numBins)
    # end getPixelBins (base class)


    def getMegaVoxelProfile(self, superVoxelBinCenters, tileProfile,
        tileInfo, fgSuperVoxel, analysis=False):
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

        if analysis and self.textureFeatures:
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
             megaVoxelProfile = np.zeros((tileInfo.numMegaVoxels, tileInfo.numSuperVoxelBins+1))
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
                    = (np.sum(tmpData!= 0, axis=1)/tmpData.shape[1]) >= tileInfo.megaVoxelThresholdTuningFactor
                for i in range(0, tileInfo.numSuperVoxelBins+1):
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
        if analysis:
            return megaVoxelProfile, fgMegaVoxel, textureFeatures
        else:
            return megaVoxelProfile, fgMegaVoxel
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