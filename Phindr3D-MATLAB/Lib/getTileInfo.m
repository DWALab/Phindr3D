function [ param ] = getTileInfo( dimSize, param )
%GETTILEINFO Computes how many pixels & stacks that needs to be retained
%based on the users choice

% Number of pixels from original image
xOffset = mod(dimSize(1),param.tileX);
yOffset = mod(dimSize(2),param.tileY);
zOffset = mod(dimSize(3),param.tileZ);


% Cropped size of new image
param.croppedX = dimSize(1) - xOffset;
param.croppedY = dimSize(2) - yOffset;
param.croppedZ = dimSize(3) - zOffset;




superVoxelXOffset = mod(param.croppedX./param.tileX,param.megaVoxelTileX); % For Megavoxels
superVoxelYOffset = mod(param.croppedY./param.tileY,param.megaVoxelTileY); % For Megavoxels

% offSet = [2:4];
% minsuperVoxelZOffset = zeros(numel(offSet),1);
% for i = 2:max(offSet)
%     minsuperVoxelZOffset(i-1) = mod(param.croppedZ./param.tileZ,offSet(i-1));
% end
% superVoxelZOffset = minsuperVoxelZOffset == 0;
% if(sum(superVoxelZOffset)>0)
%     [superVoxelZOffset, param.megaVoxelTileZ] = min(minsuperVoxelZOffset);
%     param.megaVoxelTileZ = param.megaVoxelTileZ+1;
% else
%     superVoxelZOffset = 0;
%     param.megaVoxelTileZ = 1; 
% end
superVoxelZOffset = mod(param.croppedZ./param.tileZ,param.megaVoxelTileZ);
param.origX = dimSize(1);
param.origY = dimSize(2);
param.origZ = dimSize(3);
% If offset values are even 
if(mod(xOffset,2) == 0)
    param.xOffsetStart = xOffset./2 +1;
    param.xOffsetEnd = xOffset./2;
else
    param.xOffsetStart = floor(xOffset./2)+1;
    param.xOffsetEnd = ceil(xOffset./2);
end

if(mod(yOffset,2) == 0)
    param.yOffsetStart = yOffset./2 +1;
    param.yOffsetEnd = yOffset./2;
else
    param.yOffsetStart = floor(yOffset./2)+1;
    param.yOffsetEnd = ceil(yOffset./2);
end

if(mod(zOffset,2) == 0)
    param.zOffsetStart = zOffset./2 +1;
    param.zOffsetEnd = zOffset./2;
else
    param.zOffsetStart = floor(zOffset./2)+1;
    param.zOffsetEnd = ceil(zOffset./2);
end

% Characterize super voxels
if(mod(superVoxelXOffset,2) == 0)
    param.superVoxelXOffsetStart = superVoxelXOffset./2 +1;
    param.superVoxelXOffsetEnd = superVoxelXOffset./2;
%     param.superVoxelXAddEnd = 
else
    param.superVoxelXOffsetStart = floor(superVoxelXOffset./2)+1;
    param.superVoxelXOffsetEnd = ceil(superVoxelXOffset./2);
end

% Add pixel rows if size of super voxels are not directly divisible

if(superVoxelXOffset ~= 0)
    numSuperVoxelsToAddX = param.megaVoxelTileX - superVoxelXOffset ;% Number of columns to add to the supervoxel image
%     Check if number of columns to add is odd oor even
    if(mod(numSuperVoxelsToAddX,2) == 0)
        param.superVoxelXAddStart  = numSuperVoxelsToAddX/2;
        param.superVoxelXAddEnd = numSuperVoxelsToAddX/2;
    else
        param.superVoxelXAddStart  = floor(numSuperVoxelsToAddX/2);
        param.superVoxelXAddEnd = ceil(numSuperVoxelsToAddX/2);
    end
else
    param.superVoxelXAddStart = 0;
    param.superVoxelXAddEnd = 0;
end

% Add pixel columns if size of super voxels are not directly divisible
if(superVoxelYOffset ~= 0)
    numSuperVoxelsToAddY = param.megaVoxelTileX - superVoxelYOffset ;% Number of columns to add to the supervoxel image
%     Check if number of columns to add is odd oor even
    if(mod(numSuperVoxelsToAddY,2) == 0)
        param.superVoxelYAddStart  = numSuperVoxelsToAddY/2;
        param.superVoxelYAddEnd = numSuperVoxelsToAddY/2;
    else
        param.superVoxelYAddStart  = floor(numSuperVoxelsToAddY/2);
        param.superVoxelYAddEnd = ceil(numSuperVoxelsToAddY/2);
    end
else
    param.superVoxelYAddStart = 0;
    param.superVoxelYAddEnd = 0;
end

% Add pixel columns if size of super voxels are not directly divisible
if(superVoxelZOffset ~= 0)
    numSuperVoxelsToAddZ = param.megaVoxelTileZ - superVoxelZOffset ;% Number of columns to add to the supervoxel image
%     Check if number of columns to add is odd oor even
    if(mod(numSuperVoxelsToAddZ,2) == 0)
        param.superVoxelZAddStart  = numSuperVoxelsToAddZ/2;
        param.superVoxelZAddEnd = numSuperVoxelsToAddZ/2;
    else
        param.superVoxelZAddStart  = floor(numSuperVoxelsToAddZ/2);
        param.superVoxelZAddEnd = ceil(numSuperVoxelsToAddZ/2);
    end
else
    param.superVoxelZAddStart = 0;
    param.superVoxelZAddEnd = 0;
end



if(mod(superVoxelYOffset,2) == 0)
    param.superVoxelYOffsetStart = superVoxelYOffset./2 +1;
    param.superVoxelYOffsetEnd = superVoxelYOffset./2;
else
    param.superVoxelYOffsetStart = floor(superVoxelYOffset./2)+1;
    param.superVoxelYOffsetEnd = ceil(superVoxelYOffset./2);
end

if(mod(superVoxelZOffset,2) == 0)
    param.superVoxelZOffsetStart = superVoxelZOffset./2 +1;
    param.superVoxelZOffsetEnd = superVoxelZOffset./2;
else
    param.superVoxelZOffsetStart = floor(superVoxelZOffset./2)+1;
    param.superVoxelZOffsetEnd = ceil(superVoxelZOffset./2);
end



param.numSuperVoxels = floor((param.croppedX.*param.croppedY.*param.croppedZ)./(param.tileX.*param.tileX.*param.tileZ));
param.numSuperVoxelsXY = (param.croppedX.*param.croppedY)./(param.tileX.*param.tileX);

% Old Code - May 4 16
% tmpX = (param.croppedX./param.tileX)-superVoxelXOffset;
% tmpY = (param.croppedY./param.tileY)-superVoxelYOffset;
% tmpZ = (param.croppedZ./param.tileZ)-superVoxelZOffset;

%  New Code May 4 16
tmpX = (param.croppedX./param.tileX)+superVoxelXOffset;
tmpY = (param.croppedY./param.tileY)+superVoxelYOffset;
tmpZ = (param.croppedZ./param.tileZ)+superVoxelZOffset;
% param.megaVoxelTileX = 3;
% param.megaVoxelTileY = 3;
% param.megaVoxelTileZ = 3;

param.numMegaVoxels = floor((tmpX.*tmpY.*tmpZ)./(param.megaVoxelTileY*param.megaVoxelTileX.*param.megaVoxelTileZ));
param.numMegaVoxelsXY = tmpX.*tmpY./(param.megaVoxelTileY*param.megaVoxelTileX);

% Get supervoxel locations
param.superVoxelRow = [1:param.tileX:param.croppedX];
param.superVoxelCol = [1:param.tileY:param.croppedY];
param.superVoxelZ = [1:param.tileZ:param.croppedZ];

% Get Megavoxel location

param.megaVoxelRow = [1:param.megaVoxelTileX:param.croppedX];
param.megaVoxelCol = [1:param.megaVoxelTileY:param.croppedY];
param.megaVoxelZ = [1:param.megaVoxelTileZ:param.croppedZ];

end

