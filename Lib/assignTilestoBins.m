function [ tiledImageDis ] = assignTilestoBins( tiledImage,binCenters )
%UNTITLED7 Summary of this function goes here
%   Detailed explanation goes here

numBins = size(binCenters,1);
[numTiles, numPixelTile, numChannels] = size(tiledImage);
tiledImageDis = zeros(numTiles,numPixelTile,numBins);
for iBins  = 1:numBins
    tmp = repmat(binCenters(iBins,:),numPixelTile,1);
%     tmp = repmat(tmp,numTiles,1);
    tmp = bsxfun(@minus,tiledImage,tmp);
    tmp = tmp.^2;
    tiledImageDis(:,:,iBins) = sum(tmp,3);
    
end

[~, I] = min(tiledImageDis,[],3);
tiledImageDis = I;
end

