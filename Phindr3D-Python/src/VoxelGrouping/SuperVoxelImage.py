# Tentative Super voxel class

try:
    from .VoxelGrouping import VoxelGrouping
except ImportError:
    from VoxelGrouping import VoxelGrouping

class SuperVoxelImage(VoxelGrouping):
    def __init__(self):
        super().__init__()
        self.superVoxelBinCenters = None # np array

    def getPixelBinCenters(self, x, metadata):
        # Creates x (tilesForTraining) based on data, then passes x with numBinCenters into getPixelBins
        # required parameters: pixelbincenters(voxels), randFieldID, metadata, image params (tileinfo)
        tilesForTraining = []
        # do stuff here

        # pass into getPixelBins
        self.superVoxelBinCenters = self.getPixelBins(tilesForTraining)