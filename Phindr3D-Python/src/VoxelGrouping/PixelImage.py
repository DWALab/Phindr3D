# Tentative Mega voxel class

try:
    from .VoxelGrouping import VoxelGrouping
except ImportError:
    from VoxelGrouping import VoxelGrouping

class PixelImage(VoxelGrouping):
    def __init__(self):
        super().__init__()
        self.pixelBinCenters = None # np array

    def getPixelBinCenters(self, x, metadata):
        # Same as getSuperVoxelBinCenters, but mega
        # required: randFieldID, metadata, supervoxels, image params (tileinfo)
        tilesforTraining = []

        self.pixelBinCenters = self.getPixelBins(tilesforTraining)
