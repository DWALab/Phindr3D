function [resultIM,resultRaw,metaIndexTmp] = extractImageLevelTextureFeatures(mData,allImageId,...
                                                param,outputFileName,outputDir)
%UNTITLED5 Summary of this function goes here
%   Detailed explanation goes here
disp('Started final analysis');
param.correctshade = 0;
if(param.countBackground)
    totalBins = param.numMegaVoxelBins+1;
else
    totalBins = param.numMegaVoxelBins;
end
uniqueImageID = unique(allImageId);
resultIM = zeros(numel(uniqueImageID),totalBins);
resultRaw = zeros(numel(uniqueImageID),totalBins);
metaIndexTmp = cell(numel(uniqueImageID),size(mData,2));
averageTime = 0;
h = waitbar(0,'Time remaining','Name','Extracting Image Features');

for iImages = 1:numel(uniqueImageID)
    tImageAnal = tic;
    ii = allImageId == uniqueImageID(iImages);
    [ d,param.fmt ] = getImageInformation( mData(ii,1) );
    param = getTileInfo( d,param );
    tmpInfoTable = mData(ii,1:param.numChannels);
    [ superVoxelProfile,fgSuperVoxel ] = getTileProfiles( tmpInfoTable, param.pixelBinCenters,...
        param,ii );
    [megaVoxelProfile,fgMegaVoxel] = getMegaVoxelProfile(superVoxelProfile,fgSuperVoxel,param);
    [resultIM(iImages,:), resultRaw(iImages,:)] = getImageProfile(megaVoxelProfile,fgMegaVoxel,param);
    tmp = mData(allImageId == uniqueImageID(iImages),:);
    metaIndexTmp(iImages,:) = tmp(1,:);
    %                 tmp = tmp(1,1:end-1);
    averageTime = averageTime + toc(tImageAnal);
    remainingTime = (numel(uniqueImageID) - iImages)*(averageTime/iImages);
    s = sprintf('Time remaining %7.3f min\n',remainingTime/60);
    waitbar(iImages./numel(uniqueImageID),h,s);
%     fprintf('\b\b\b\b\b\b\b\b%7.3f%%',iImages*100./numel(uniqueImageID));
end
numRawMV = sum(resultRaw,2);
close(h);

clear averageTime remTime str;
disp('Completed image level analysis....');
% Compute well level data
%             disp('Computing well level data....');
% Output Results
disp('Writing to output file....');
h = waitbar(0,'Writing to output file');
dataHeaderIM = cell(1,size(resultIM,2));
for i = 1:size(resultIM,2)
    dataHeaderIM{1,i} = ['MV' num2str(i)];
end
% Remove ImageID if existis in Metadata
ii = strcmpi(param.metaDataHeader,'ImageID');
param.metaDataHeader = param.metaDataHeader(~ii);
metaIndexTmp = metaIndexTmp(:,~ii);
resultTmp = [uniqueImageID numRawMV resultIM];
outputHeader = [param.metaDataHeader(1,:) {'ImageID' 'NumMV'} dataHeaderIM];
writestr(fullfile(outputDir,outputFileName),outputHeader,'Overwrite');
waitbar(.5,h);
writestr(fullfile(outputDir,outputFileName),[metaIndexTmp cellstr(num2str([resultTmp],'%f\t'))],'append');
parameterFileName = strrep(outputFileName,'.txt','.mat');
save(fullfile(outputDir,parameterFileName),'param');
waitbar(1,h);close(h);
disp('Completed writing output file');
end

