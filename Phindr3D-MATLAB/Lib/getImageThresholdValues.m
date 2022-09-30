function param = getImageThresholdValues(mData,allImageId,param)
%getImageThresholdValues Gets image threshold values for the dataset
%   Detailed explanation goes here


intensityThresholdValues = nan(5000,param.numChannels);
startVal = 1;
endVal = 1;
h = waitbar(0,'Selecting Intensity Threhold...');
% fprintf('Entering Threshold........................');
for iImages =  1:numel(param.randFieldID)
    ii  = allImageId == param.randFieldID(iImages);
%     disp( mData{1,1})
    xx = mData(ii,1);
    if(isempty(xx))
        disp('SSS')
    end
    [ d,param.fmt ] = getImageInformation( mData(ii,1) );
    param = getTileInfo( d,param );
    iTmp = getIndividualChannelThreshold(mData(ii,...
        1:param.numChannels),param,ii);
    intensityThresholdValues(startVal:endVal + size(iTmp,1)-1,:) = iTmp;
    startVal = startVal + size(iTmp,1);
    endVal = endVal + size(iTmp,1);
    waitbar(iImages./numel(param.randFieldID),h);
end
ii = isnan(intensityThresholdValues(:,1))==0;
param.intensityThresholdValues = intensityThresholdValues(ii,:);
close(h);
end

