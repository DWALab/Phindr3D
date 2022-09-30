function [ superVoxelProfile, fgSuperVoxel,TASScores ] = getTileProfiles( filenames, pixelBinCenters, param,ii )
%getSuperVoxelProfiles:- Compute slow level categorical features for
%supervoxels
% The function assigns categories for each pixel and computes supervoxel
% profile for each supervoxel
% Inputs:
% filenames - Image file names images x numchannels
% pixelBinCenters - Location of pixel categories: number of bins x number
% of channels
% Output:
% superVoxelProfile: number of supervoxels by number of supervoxelbins plus
% a background
% fgSuperVoxel: Foreground supervoxels - At lease one of the channles
% should be higher than the respective thrshold
% TASScores: If TAS score is sleected




% Get Parameters
numTilesXY = (param.croppedX.*param.croppedY)./(param.tileX.*param.tileY);
% croppedX = param.croppedX;
% croppedY = param.croppedY;
% % croppedZ = param.croppedZ;
% intensityThreshold = param.intensityThreshold;
% % [tileSize] = [param.tileX param.tileY param.tileZ];
% 
% xOffsetStart = param.xOffsetStart;
% xOffsetEnd = param.xOffsetEnd;
% yOffsetStart = param.yOffsetStart;
% yOffsetEnd = param.yOffsetEnd;
% zOffsetStart = param.zOffsetStart;
% zOffsetEnd = param.zOffsetEnd;


filenames = filenames(param.zOffsetStart:end-param.zOffsetEnd,:);% Keep z stacks that are divisible by stack count
sliceCounter = 0;
startVal = 1;
endVal = numTilesXY;

startCol = 1;
endCol = param.tileX.*param.tileY;
if(param.intensityNormPerTreatment)
    grpVal = unique(param.grpIndicesForIntensityNormalization(ii));
end
% Store super vozel profiles here:
superVoxelProfile = zeros(param.numSuperVoxels,param.numVoxelBins+1);% Initialize supervoxel
fgSuperVoxel = zeros(param.numSuperVoxels,1);
cnt = 1;
if(param.computeTAS)
    categoricalImage = zeros(param.croppedX,param.croppedY,param.croppedZ);
end
% Loop over file names & extract super voxels
tmpData = zeros(numTilesXY,param.tileX.*param.tileY.*param.tileZ);
for iImages = 1:size(filenames,1) 
    sliceCounter = sliceCounter+1;
    croppedIM = zeros(param.origX,param.origY,param.numChannels);    
    for jChannels = 1:param.numChannels
        
        if(param.intensityNormPerTreatment)
             croppedIM(:,:,jChannels) = rescaleIntensity(imread(filenames{iImages,jChannels},param.fmt),...
                 param.lowerbound(grpVal,jChannels),param.upperbound(grpVal,jChannels));
         else
             croppedIM(:,:,jChannels) = rescaleIntensity(imread(filenames{iImages,jChannels},param.fmt),...
                 param.lowerbound(:,jChannels),param.upperbound(:,jChannels));
         end
        
    end   
    croppedIM = croppedIM(param.xOffsetStart:(end - param.xOffsetEnd),param.yOffsetStart:(end - param.yOffsetEnd),:);
%     if(param.correctshade)
%         croppedIM  = croppedIM./param.allRef;
%     end    
    x = reshape(croppedIM,param.croppedX.*param.croppedY,param.numChannels); 
    fg = sum(bsxfun(@gt,x,param.intensityThreshold),2) >= param.numChannels/3;
%     xFg = x(fg,:);   
    [~, pixelCategory] = min((bsxfun(@plus,param.pixelBinCenterDifferences,dot(x(fg,:),x(fg,:),2)) -2.*(x(fg,:)*pixelBinCenters')),...
                    [],2);
    x = uint8(zeros(param.croppedX.*param.croppedY,1));
    x(fg,:) = pixelCategory;
    
%     if(param.showImage && (cnt ==9))  
%         figure;imagesc(reshape(x,param.croppedX,param.croppedY));
%        
%         figure;imshow(uint16(croppedIM(:,:,:)),[]);
%         if(param.numChannels>1)
%             for jj = 2:param.numChannels+1
%                 figure;imshow(croppedIM(:,:,jj-1),[]);
%             end
%         end
%     end
    if(param.computeTAS)
        categoricalImage(:,:,iImages) = reshape(x,param.croppedX,param.croppedY);
    end
                                                                
    clear xFg fg minDis croppedIM pixelCategory;    
    if(sliceCounter == param.tileZ)        
        fgSuperVoxel(startVal:endVal,1) = (sum(tmpData ~= 0,2)./size(tmpData,2)) >= param.superVoxelThresholdTuningFactor;
        
        for i = 1:param.numVoxelBins+1
            superVoxelProfile(startVal:endVal,i) = sum(tmpData == i-1,2);% A value of zero indicates background pixels
        end
        
        sliceCounter = 0;
        startVal = startVal+numTilesXY;
        endVal = endVal+numTilesXY;
%         startVal = 1;
%         endVal = numTilesXY;
        startCol = 1;
        endCol = param.tileX.*param.tileY;
        tmpData = zeros(numTilesXY,param.tileX.*param.tileY.*param.tileZ);
    else
%         superVoxelProfile(startVal:endVal,startCol:endCol) = im2col(reshape(x,...
%                                                                 croppedX,croppedY),[param.tileX param.tileY],...
%                                                                 'distinct')';
        tmpData(:,startCol:endCol) = im2col(reshape(x,...
                                                                param.croppedX,param.croppedY),[param.tileX param.tileY],...
                                                                'distinct')';
        startCol = startCol+ (param.tileX.*param.tileY);
        endCol = endCol + (param.tileX.*param.tileY);
        
    end
    cnt = cnt+1;
end


if(~param.countBackground)
    superVoxelProfile = superVoxelProfile(:,2:end);
end
superVoxelProfile = bsxfun(@rdivide,superVoxelProfile,sum(superVoxelProfile,2));
superVoxelProfile(isnan(superVoxelProfile)) = 0;
if(param.computeTAS)
    TASScores = getCategoricalTASScores( categoricalImage, param.numVoxelBins );
else
    TASScores = zeros(1,27*param.numVoxelBins);
end
fgSuperVoxel = logical(fgSuperVoxel);
end

