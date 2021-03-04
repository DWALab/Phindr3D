function image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,stack2View,typeOfView)
% getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
%                                 chanInfo,stack2View,typeOfView)
% 
%  Selects image based on specific image ID. The functions is used as a
%  support for PhindR GUI program
%
% Input parameters
%
% mData -Metadata cell array consisting of individual image information
%           in each row
%
% metaHeader - Associated metadata header
%
% param - Parameter file (Structure variable)
% 
% imageID2View - Image id selected to view
% 
% imageID - List of all image ID. Column vector
% 
% chanInfo - Structure variable having specific information about channels
% 
% stack2View - If viewing single slice then the stack number to view
% typeOfView - Montage, MIP. Any other choice defaults to single plane
% ---------------------------------------
% Created: Santosh Hariharan 
% Date: Aug 13 2018
% DWA Lab, University Of Toronto
% ---------------------------------------
ii = imageID == imageID2View;
stackCol = or(strcmpi(metaHeader,'Stack'),strcmpi(metaHeader,'Stacks'));
stackCol = str2num(char(mData(ii,stackCol)));
[~,stackSort] = sort(stackCol,'ascend');
imageFileNames = mData(ii,chanInfo.channelColNumber);
imageFileNames = imageFileNames(stackSort,:);
if(stack2View <=0 || stack2View >= sum(ii))
    stack2View = 1;
end

% Extract Bounds based on imageID
if(param.intensityNormPerTreatment)
    grpVal = unique(param.grpIndicesForIntensityNormalization(ii));
    lowerbound = param.lowerbound(grpVal,:)';
    upperbound = param.upperbound(grpVal,:)';
else
    lowerbound = param.lowerbound';
    upperbound = param.upperbound';
end
boundValues = [lowerbound upperbound];


imageInformation = imfinfo(imageFileNames{1,1});
if(strcmpi(typeOfView,'montage'))
    image2Display = zeros(imageInformation.Width,imageInformation.Height,...
        numel(chanInfo.channelColNumber),sum(ii));
    for iSlices = 1:sum(ii)        
        image2Display(:,:,:,iSlices)  = getMerged3DImage(imageFileNames(iSlices,:),chanInfo.channelColors,...
           boundValues,param.intensityThreshold);        
    end
   
    
elseif(strcmpi(typeOfView,'MIP'))
    image2Display = zeros(imageInformation.Width,imageInformation.Height,...
                            numel(chanInfo.channelColNumber));
    for iChannels = 1:numel(chanInfo.channelColNumber)
        image2Display(:,:,iChannels) = getMIPImage(imageFileNames(:,iChannels));
    end
    image2Display = getMerged3DImage(image2Display,chanInfo.channelColors,...
            boundValues,param.intensityThreshold);
    
else
    image2Display = getMerged3DImage(imageFileNames(stack2View,:),chanInfo.channelColors,...
            boundValues,param.intensityThreshold);
       
end



end


