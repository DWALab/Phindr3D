function [im3D] = mergeChannels(imMultiChannel,colors)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
[m,n,numChannels] = size(imMultiChannel);
im3D = zeros(m,n,3);
for jChannel = 1:numChannels

    maxVal = max(max(imMultiChannel(:,:,jChannel)));
    minVal= min(min(imMultiChannel(:,:,jChannel)));
    maxMin = abs(maxVal - minVal);
    im = (imMultiChannel(:,:,jChannel) - minVal)./maxMin;
    im(im>1) = 1;
    im(im<0) = 0;
%     im = imadjust(im);
    im3D(:,:,1) = im3D(:,:,1) + colors(jChannel,1).*im;
    im3D(:,:,2) = im3D(:,:,2) + colors(jChannel,2).*im;
    im3D(:,:,3) = im3D(:,:,3) + colors(jChannel,3).*im;
end
end

