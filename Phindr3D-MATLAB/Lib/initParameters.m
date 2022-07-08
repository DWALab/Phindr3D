function [ param ] = initParameters()
%initParameters Initiates parameters and returns a structured array
%   Detailed explanation goes here


param.tileX = 10;
param.tileY = 10;
param.tileZ = 3;
param.intensityThresholdTuningFactor = .5;
param.numVoxelBins = 20;
param.numSuperVoxelBins = 15;
param.numMegaVoxelBins = 40;
param.minQuantileScaling = .5;
param.maxQuantileScaling = .5;
param.randTrainingSuperVoxel = 10000;
param.superVoxelThresholdTuningFactor = .5;
param.megaVoxelTileX = 5;
param.megaVoxelTileY = 5;
param.megaVoxelTileZ = 2;
param.countBackground = false;
param.megaVoxelThresholdTuningFactor = .5;
param.pixelsPerImage = 200;
param.randTrainingPerTreatment = 1;
param.randTrainingFields = 5;
param.showImage = 0;
param.startZPlane = 1;
param.endZPlane = 500;
param.numRemoveZStart = 1;
param.numRemoveZEnd = 1;
param.computeTAS = 0;
param.showImage = 0;
param.trainingPerColumn = false;
param.intensityNormPerTreatment = false;
param.treatmentColNameForNormalization = ''; % Default Change Later
param.trainingColforImageCategories = '';
param.superVoxelPerField = floor(param.randTrainingSuperVoxel./param.randTrainingFields);
end

