function [ imMIP ] = getMIPImage( imfiles )
%getMIPImage Creates maximum intensity projected images for a set of image
%files in imfiles

format = regexpi(imfiles{1,1},'\.','split');

format = format{1,end};

numzPlanes = size(imfiles,1);
info = imfinfo(imfiles{1,1},format);

imMIP = -inf.*ones(info.Height,info.Width);

for i = 1:numzPlanes
    tmp = imread(imfiles{i,1},format);
    tmp = medfilt2(double(tmp));
    imMIP = max(imMIP,tmp);
end
end

