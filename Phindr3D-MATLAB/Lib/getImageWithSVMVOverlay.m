function IM = getImageWithSVMVOverlay(IM,param,type)
%getImageWithSVMVOverlay Summary of this function goes here
%   Detailed explanation goes here


% param.tileX = 10;
% param.tileY = 10;
% param.megaVoxelTileX = 5;
% param.megaVoxelTileY = 5;
if(strcmpi(type,'SV'))
    IM(1:param.tileX:end,:,:) = .7;
    IM(:,1:param.tileY:end,:) = .7;
else
    IM(1:param.tileX*param.megaVoxelTileX:end,:,:) = 1;
    IM(:,1:param.tileY*param.megaVoxelTileY:end,:) = 1;
end
% imxy = zeros(size(IM,1),size(IM,2));
end

