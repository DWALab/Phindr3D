function imthreshold = getImageThreshold(IM)


maxBins = 256;
% IM = double(IM);
[freq,binCenters] = hist(IM(:),maxBins);
meanIntensity = mean(IM(:));
clear IM;
numThresholdParam = length(freq);

binCenters  = binCenters - meanIntensity;
den1 = sqrt(binCenters.^2*freq');
numAllPixels = sum(freq);
covarMat = zeros(numThresholdParam,1);
for iThreshold = 1:numThresholdParam
    
    numThreshPixels = sum(freq(binCenters>binCenters(iThreshold)));
    den2 = sqrt((((numAllPixels-numThreshPixels)*(numThreshPixels))/numAllPixels));
    covarMat(iThreshold,1) = (binCenters*(freq.*(binCenters>binCenters(iThreshold)))')./(den1.*den2);
end
[~,imthreshold] = max(covarMat);
imthreshold = binCenters(imthreshold) + meanIntensity;
end