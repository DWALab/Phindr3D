function [imageProfile, rawProfile] = getImageProfile(megaVoxelProfile,fgMegaVoxel,param)
% getImageProfile - Provides a multiparametric representation of images
%                   based on megavoxel categories
% 


% x = megaVoxelProfile(fgMegaVoxel,:); % Consider only foreground mega voxels
a = bsxfun(@plus,dot(param.megaVoxelBincenters,param.megaVoxelBincenters,2)',...
                     dot(megaVoxelProfile(fgMegaVoxel,:),megaVoxelProfile(fgMegaVoxel,:),2)) -2*(megaVoxelProfile(fgMegaVoxel,:)*param.megaVoxelBincenters');
[~, minDis] = min(a,[],2);
x = zeros(size(megaVoxelProfile,1),1);
x(fgMegaVoxel,1) = minDis;
% x = minDis;
numbins = param.numMegaVoxelBins;
tmp = zeros(1,numbins+1);

for i = 1:numbins+1
    tmp(:,i) = sum(x(fgMegaVoxel,1) == i-1);
end
imageProfile = tmp;
if(~param.countBackground)
    rawProfile = imageProfile(:,2:end);
    imageProfile = imageProfile(:,2:end);
else
    rawProfile = imageProfile;
end

imageProfile = bsxfun(@rdivide,imageProfile,sum(imageProfile,2));
% imageProfile(isnan(imageProfile)) = 0;
end