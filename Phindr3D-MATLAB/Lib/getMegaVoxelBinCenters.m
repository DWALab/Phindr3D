function [param] = getMegaVoxelBinCenters(mData,allImageId,param)
%getMegaVoxelBinCenters Computes bincenters for Mega Voxels
% mData  - Metadata
% allImageID - Image ID's of each image stack
% param - All parameters
% Output
% param - Appended parameters
% Author  - Santosh Hariharan (DWA Lab) 
% Date Created - May 30 2018
% 
% fprintf('Computing megavoxel bin centers............');
megaVoxelforTraining = [];
totalIterations = numel(param.randFieldID)+1;
h = waitbar(0,'Collecting MegaVoxel Information');
for iImages = 1:numel(param.randFieldID)
    ii = allImageId == param.randFieldID(iImages);
    [ d,param.fmt ] = getImageInformation( mData(ii,1) );
    param = getTileInfo( d,param );
    tmpInfoTable = mData(ii,1:param.numChannels);
    [ superVoxelProfile,fgSuperVoxel ] = getTileProfiles( tmpInfoTable, param.pixelBinCenters, param, ii );
    [megaVoxelProfile,fgMegaVoxel] = getMegaVoxelProfile(superVoxelProfile,fgSuperVoxel,param);
    megaVoxelforTraining = [megaVoxelforTraining;megaVoxelProfile(fgMegaVoxel,:)];
    waitbar(iImages./totalIterations,h);
%     fprintf('\b\b\b\b\b\b\b\b%7.3f%%',iImages*100./numel(randFieldID));
end
% fprintf('\n');
waitbar((iImages+1)./totalIterations,h,'Computing MegaVoxel bin centers');
param.megaVoxelBincenters = getPixelBins( megaVoxelforTraining,param.numMegaVoxelBins);
%                 disp('Competed computing mega voxel bin centers');
% clear megaVoxelforTraining tmpInfoTable selBlocks tmp tileProfile fgSuperVoxel
close(h);
end

