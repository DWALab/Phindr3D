function [megaVoxelProfile, fgMegaVoxel] = getMegaVoxelProfile(tileProfile,fgSuperVoxel,param)
% 



% fgSuperVoxel = logical(fgSuperVoxel);
% pixelBinCenters = param.supervoxelBincenters;
% x = tileProfile(fgSuperVoxel,:);
a = bsxfun(@plus,dot(param.supervoxelBincenters,param.supervoxelBincenters,2)',...
                            dot(tileProfile(fgSuperVoxel,:),tileProfile(fgSuperVoxel,:),2))...
                            -2*(tileProfile(fgSuperVoxel,:)*param.supervoxelBincenters');
[~, minDis] = min(a,[],2);
x = zeros(size(tileProfile,1),1);
x(fgSuperVoxel,1) = minDis;

x = reshape(x,param.croppedX./param.tileX,param.croppedY./param.tileY,param.croppedZ./param.tileZ);
if(param.showImage)
    
    %        subplot(param.numChannels+1,1,1);imshow(reshape(x,param.croppedX,param.croppedY),[]);
    figure;imagesc(x(:,:,3));
    
    
end
% Old Code - May 4 16
% x = x(param.superVoxelXOffsetStart:(end - param.superVoxelXOffsetEnd),...
%                     param.superVoxelYOffsetStart:(end - param.superVoxelYOffsetEnd),...
%                     param.superVoxelZOffsetStart:(end - param.superVoxelZOffsetEnd));
% new Code - may 4 16

x = cat(1,zeros(param.superVoxelXAddStart,size(x,2),size(x,3)),x,zeros(param.superVoxelXAddEnd,size(x,2),size(x,3)));
x = cat(2,zeros(size(x,1),param.superVoxelYAddStart,size(x,3)),x,zeros(size(x,1),param.superVoxelYAddEnd,size(x,3)));
x = cat(3,zeros(size(x,1),size(x,2),param.superVoxelZAddStart),x,zeros(size(x,1),size(x,2),param.superVoxelZAddEnd));
% m = size(x,1);
% x = cat(2,zeros(m,param.superVoxelYOffsetStart,size(x,3)),x,zeros(m,param.superVoxelYOffsetEnd,size(x,3)));
x = uint8(x);
param.numMegaVoxelsXY = size(x,1).*size(x,2)./(param.megaVoxelTileY*param.megaVoxelTileX);
param.numMegaVoxels = (param.numMegaVoxelsXY*size(x,3))./(param.megaVoxelTileZ);
sliceCounter = 0;tmp=[];
startVal = 1;
endVal = param.numMegaVoxelsXY;
% megaVoxelProfile = zeros(param.numMegaVoxels,(param.megaVoxelTileX.*param.megaVoxelTileY.*param.megaVoxelTileZ));
try
megaVoxelProfile = zeros(param.numMegaVoxels,param.numSuperVoxelBins+1);
catch expc
    disp('@@');
end
fgMegaVoxel = zeros(param.numMegaVoxels,1);
for iSuperVoxelImagesZ = 1:size(x,3)
    sliceCounter = sliceCounter+1;
    tmp1 = im2col(x(:,:,iSuperVoxelImagesZ),[param.megaVoxelTileX param.megaVoxelTileY],'distinct')';
    tmp = [tmp tmp1];
    if(sliceCounter == param.megaVoxelTileZ)
        for i = 1:param.numSuperVoxelBins+1
            megaVoxelProfile(startVal:endVal,i) = sum(tmp == i-1,2);% A value of zeros indicates background supervoxel
        end
        fgMegaVoxel(startVal:endVal,1) = (sum(tmp ~= 0,2)./size(tmp,2))...
                                                   >= param.megaVoxelThresholdTuningFactor;
%         megaVoxelProfile(startVal:endVal,:) = tmp;
        sliceCounter = 0;
        tmp = [];
        startVal = startVal+param.numMegaVoxelsXY;
        endVal = endVal+param.numMegaVoxelsXY;
    end
end


% fgMegaVoxel = (sum(megaVoxelProfile ~= 0,2)./size(megaVoxelProfile,2)) >= param.megaVoxelThresholdTuningFactor;
% numbins = param.numSuperVoxelBins;% Accounts for Mega voxels with zero intensity 
% tmp = zeros(size(megaVoxelProfile,1),numbins+1);
% for i = 1:numbins+1
%     tmp(:,i) = sum(megaVoxelProfile == i-1,2);
% end
% megaVoxelProfile = megaVoxelProfile(fgMegaVoxel,:);
% megaVoxelProfile = tmp;
if(~param.countBackground)
    megaVoxelProfile = megaVoxelProfile(:,2:end);
end
megaVoxelProfile = bsxfun(@rdivide,megaVoxelProfile,sum(megaVoxelProfile,2));
% megaVoxelProfile(isnan(megaVoxelProfile)) = 0;
fgMegaVoxel = logical(fgMegaVoxel);
end