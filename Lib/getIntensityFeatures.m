function [allHeader,allData] = getIntensityFeatures(metadataFileRaw,metadataFilenameLabel,uImageID)

param.channelDiscarded=[];
[metadataLabel,~,~,imageIDLabel] = getPlateInfoFromMetadatafile(metadataFilenameLabel,param);
[metadataRaw,headerRaw,~,imageIDRaw] = getPlateInfoFromMetadatafile(metadataFileRaw,param);

stkCol = strcmpi(headerRaw,'Stack');
allFeatures = nan(numel(uImageID),4);
h = waitbar(0,'Running Morphology');
for i = 1:numel(uImageID)
    ii = imageIDRaw == uImageID(i);
    if(sum(ii) ==0)
        continue;
    end
    stk = str2num(char(metadataRaw(ii,stkCol)));
    stk2pick = floor((max(stk) - min(stk))./2);
    jj = stk == min(stk)+stk2pick;
    channelCol = metadataRaw(ii,1:3);
    channelCol = channelCol(jj,:);
    % Label image
    kk = imageIDLabel == uImageID(i);
    labelImage = metadataLabel{kk,1};
    labelImage = imread(labelImage,'tiff');
    labelImage = labelImage>0;
    labelImage = imerode(labelImage,ones(20));
    labelImageEroded = imerode(labelImage,ones(60));
%     figure;imshow(labelImage,[]);
%     figure;imshow(labelImageEroded,[]);
%     figure;imshow(bwperim(labelImage-labelImageEroded),[]);
    
    for k =  1:3
        rawImage = double(imread(channelCol{1,k},'tiff'));
        im1 = labelImageEroded.*rawImage;
        int1 = sum(im1(:))./sum(labelImageEroded(:));
        im1 = (labelImage-labelImageEroded).*rawImage;
        l = labelImage-labelImageEroded;
        int2 = sum(im1(:))./sum(l(:));
        allFeatures(i,k) = int2/int1;
    end
    allFeatures(i,4) = max(stk) - min(stk);
    waitbar(i/numel(uImageID),h);
% %     Raw image
%     rawImage = imread(channelCol{1,3},'tiff');
%     figure;imshow(rawImage,[]);
%     
%     re
end
close(h);
% Get MIP 
allFeaturesInt = nan(numel(uImageID),3);
h = waitbar(0,'Fetching MIP intensity');
for i = 1:numel(uImageID)
    ii = imageIDRaw == uImageID(i);
    if(sum(ii) ==0)
        continue;
    end
    stk = str2num(char(metadataRaw(ii,stkCol)));
    stk2pick = floor((max(stk) - min(stk))./2);
    jj = stk == min(stk)+stk2pick;
    channelCol = metadataRaw(ii,1:3);
%     channelCol = channelCol(jj,:);
    
    % Label image
    kk = imageIDLabel == uImageID(i);
    labelImage = metadataLabel{kk,1};
    labelImage = imread(labelImage,'tiff');
    labelImage = labelImage>0;
%     labelImage = imerode(labelImage,ones(20));
   
%     figure;imshow(labelImage,[]);
%     figure;imshow(labelImageEroded,[]);
%     figure;imshow(bwperim(labelImage-labelImageEroded),[]);
    
    for k =  1:3        
        rawImage = getMIPImage(channelCol(:,k));
        im1 = labelImage.*rawImage;        
        allFeaturesInt(i,k) = sum(im1(:))./sum(labelImage(:));
    end
    waitbar(i/numel(uImageID),h);
%     Raw image
%     rawImage = imread(channelCol{1,3},'tiff');
%     figure;imshow(rawImage,[]);
%     
%     re
end
close(h);

allHeader = {'Ch1Int' 'Ch2Int' 'Ch3Int' 'Ch1Ratio' 'Ch2Ratio' 'Ch3Ratio' 'NumPlanes'};
allData = [allFeaturesInt allFeatures];
end

