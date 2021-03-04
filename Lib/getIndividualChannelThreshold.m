function thresh = getIndividualChannelThreshold(filenames,param,ii)

% 
% filenames = filenames(param.zOffsetStart:end-param.zOffsetEnd,:);% Keep z stacks that are divisible by stack count
numberChannels = size(filenames,2);
% method = 'MCT';
thresh = zeros(size(filenames));
% thresh = zeros(1,param.numChannels);
% Read images per channel
if(nargin<3)
    ii = true(size(filenames,1));
end
if(param.intensityNormPerTreatment)
    grpVal = unique(param.grpIndicesForIntensityNormalization(ii));
end
for iChannels = 1:numberChannels
%     IM = zeros(param.origX,param.origY,size(filenames,1));
%     imageThresh = zeros(size(filenames,1),1);
    for iImages = 1:size(filenames,1)
%         IM(:,:,iImages) = imread(filenames{iImages,iChannels},'tiff');
        IM = imread(filenames{iImages,iChannels},param.fmt);
        IM = IM(param.xOffsetStart:(end - param.xOffsetEnd),param.yOffsetStart:(end - param.yOffsetEnd));
        
%         Add noise - to be removed later
        
%         if(param.correctshade)
%             IM = double(IM)./param.allRef(:,:,iChannels);
%             thresh(iImages,iChannels) = getImageThreshold(IM);
%         else
         if(param.intensityNormPerTreatment)
             IM = rescaleIntensity(IM,param.lowerbound(grpVal,iChannels),param.upperbound(grpVal,iChannels));
         else
             IM = rescaleIntensity(IM,param.lowerbound(:,iChannels),param.upperbound(:,iChannels));
         end
            
            thresh(iImages,iChannels) = getImageThreshold(double(IM));
%         end
        
    end
%     IM = IM(param.xOffsetStart:(end - param.xOffsetEnd),param.yOffsetStart:(end - param.yOffsetEnd),:);
%     thresh(1,iChannels) = getImageThreshold(IM);
    clear IM;
end




end