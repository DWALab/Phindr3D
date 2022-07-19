# Tentative Mega voxel class

try:
    from .VoxelGrouping import VoxelGrouping
except ImportError:
    from VoxelGrouping import VoxelGrouping

class MegaVoxelImage(VoxelGrouping):
    def __init__(self):
        super().__init__()
        self.megaVoxelBinCenters = None # np array

    def getMegaVoxelBinCenters(self, x, metadata):
        # Same as getSuperVoxelBinCenters, but mega
        # required: randFieldID, metadata, supervoxels, image params (tileinfo)
        megaVoxelsforTraining = []

        # megaVoxelBinCenters is an np array that represents the megavoxels
        self.megaVoxelBinCenters = self.getPixelBins(megaVoxelsforTraining)
