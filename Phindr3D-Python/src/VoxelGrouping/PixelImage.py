# Tentative Mega voxel class

try:
    from .VoxelGrouping import VoxelGrouping
    from ..Data import *
except ImportError:
    from VoxelGrouping import VoxelGrouping

class PixelImage(VoxelGrouping):
    def __init__(self):
        super().__init__()
        self.pixelBinCenters = None # np array

    def getPixelBinCenters(self, x, metadata):
        # required: randFieldID, metadata, image params (tileinfo)
        pixelsForTraining = np.zeros((300000, metadata.GetNumChannels()))
        startVal = 0
        endVal = 0
        for i, id in enumerate(metadata.getTrainingFields()):
            d = metadata.getImageInformation(metadata.GetImage(id))
            info = metadata.getTileInfo(d, metadata.theTileInfo)

        self.pixelBinCenters = self.getPixelBins(pixelsForTraining)

    def getTrainingPixels(self, image, metadata, randZ, training, tileinfo):
        slices = image.stackLayers.keys()
        slices = np.array([slices[i] for i in metadata.Generator.choice(len(slices), size=randZ, replace=False, shuffle=False)])
        trPixels = np.zeros((training.pixelsPerImage*randZ, metadata.GetNumChannels()))
        startVal = 0
        if metadata.intensityNormPerTreatment:
            grpVal = np.argwhere(metadata.GetTreatmentTypes() == image.GetTreatment()[0])
        slices = slices[0:(len(slices)//2)]
        for zplane in slices:
            croppedIM = np.zeros((tileinfo.origX, tileinfo.origY, metadata.GetNumChannels()))
            for jChan in range(metadata.GetNumChannels):
                if metadata.intensityNormPerTreatment:
                    croppedIM[:,:, jChan] = training.rescaleIntensity() # add params later
                else:
                    croppedIM[:,:, jChan] = training.rescaleIntensity() # add params later
            xEnd = -tileinfo.xOffsetEnd
            if xEnd == -0:
                xEnd = None
            yEnd = -tileinfo.yOffsetEnd
            if yEnd == -0:
                yEnd = None
            croppedIM = croppedIM[tileinfo.xOffsetStart:xEnd, tileinfo.yOffsetStart:yEnd, :]
            croppedIM = np.reshape(croppedIM, (tileinfo.croppedX*tileinfo.croppedY, metadata.GetNumChannels()))
            croppedIM = croppedIM[np.sum(croppedIM > metadata.intensityThreshold, axis=1) > metadata.GetNumChannels()/3, :]
            # croppedIM = selectPixelsbyweights(croppedIM) uncomment when implemented
            if croppedIM.shape[0] >= training.pixelsPerImage:
                trPixels[startVal:startVal + training.pixelsPerImage, :] = np.array([croppedIM[i,:] for i in metadata.Generator.choice(croppedIM.shape[0],size=training.pixelsPerImage, replace=False, shuffle=False)])
                startVal += croppedIM.shape[0]
        if trPixels.size == 0:
            trPixels = np.zeros((training.pixelsPerImage*randZ, metadata.GetNumChannels()))
        return trPixels