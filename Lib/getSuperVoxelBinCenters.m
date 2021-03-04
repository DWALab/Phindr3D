function [param] = getSuperVoxelBinCenters(mData,allImageId,param)
%getSuperVoxelBinCenters Computes bincenters for Super Voxels
% mData  - Metadata
% allImageID - Image ID's of each image stack
% param - All parameters
% Output
% param - Appended parameters
% Author  - Santosh Hariharan (DWA Lab) 
% Date Created - May 30 2018
% 
param.pixelBinCenterDifferences = dot(param.pixelBinCenters,param.pixelBinCenters,2)';
tilesForTraining = [];


totalIterations = numel(param.randFieldID)+1;
h = waitbar(0,'Collecting Super Voxel Information');
for iImages = 1:numel(param.randFieldID)
    ii = allImageId == param.randFieldID(iImages);
    [ d,param.fmt ] = getImageInformation( mData(ii,1) );
    param = getTileInfo( d,param );
    tmpInfoTable = mData(ii,1:param.numChannels);
    [ superVoxelProfile,fgSuperVoxel ] = getTileProfiles( tmpInfoTable, param.pixelBinCenters, param,ii );
    tmp = superVoxelProfile(fgSuperVoxel,:);
    if(param.superVoxelPerField>size(tmp,1))
        tilesForTraining = [tilesForTraining;tmp(:,:)];
    else
        selBlocks  = randperm(size(tmp,1),param.superVoxelPerField);
        tilesForTraining = [tilesForTraining;tmp(selBlocks,:)];
    end
    %             fprintf('Time taken for field %f\n',toc(tImageAnal));
%     fprintf('\b\b\b\b\b\b\b\b%7.3f%%',iImages*100./numel(randFieldID));
    waitbar(iImages./totalIterations,h);
end
fprintf('\n');
waitbar((iImages+1)./totalIterations,h,'Computing SuperVoxel bin centers');
param.supervoxelBincenters = getPixelBins( tilesForTraining,param.numSuperVoxelBins);
close(h);
% clear tilesForTraining tmpInfoTable selBlocks tmp superVoxelProfile fgSuperVoxel
end

