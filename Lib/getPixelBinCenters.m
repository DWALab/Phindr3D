function param = getPixelBinCenters(mData, allImageId, param)
%getPixelBinCenters Computes bincenters for pixels
% mData  - Metadata
% allImageID - Image ID's of each image stack
% param - All parameters
% Output
% param - Appended parameters
% Author  - Santosh Hariharan (DWA Lab) 
% Date Created - May 30 2018
% 

pixelsForTraining = zeros(300000,param.numChannels);
startVal = 1;
endVal=1;
h = waitbar(0,'Collecting Voxel Information');
totalIterations = numel(param.randFieldID)+1;
for iImages = 1:numel(param.randFieldID)
    ii = allImageId == param.randFieldID(iImages);
    [ d,param.fmt ] = getImageInformation( mData(ii,1) );
    param = getTileInfo( d,param );
    param.randZForTraining = floor(.5*sum(ii));
    tmpInfoTable = mData(ii,1:param.numChannels);
    iTmp= getTrainingPixels(tmpInfoTable,param,ii);
    pixelsForTraining(startVal:endVal+size(iTmp,1)-1,:) = iTmp;
    startVal = startVal + size(iTmp,1);
    endVal = endVal + size(iTmp,1);
    waitbar(iImages./totalIterations,h);
end

pixelsForTraining = pixelsForTraining(sum(pixelsForTraining,2) > 0,:);
waitbar((iImages+1)./totalIterations,h,'Computing Voxel Bin Centers');
[ param.pixelBinCenters ] = getPixelBins( pixelsForTraining,param.numVoxelBins);
close(h);

end



