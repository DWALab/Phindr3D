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
