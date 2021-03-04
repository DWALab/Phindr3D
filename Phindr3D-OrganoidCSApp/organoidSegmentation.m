%% Script to wite out cropped oncogene images
%  To run file
% Set segmentation parameters
% Select metadatafile (created by extractor) and follow prompts
% Dependency - Image processing tool box
%% Segmentation Parameters

min_area_spheroid = 200; % Minimum Area
intensity_threshold = 500; % Minimum Intensity (Average MIP Intensity)
radius_spheroid = 75; % Approx Radius in pixels
smoothin_param=.01; % Smoothing Factor
scale_spheroid =1; % Scale Factor
entropy_threshold = 1;

%% Metadata Extraction

[metadataFileName,param.rootDir] = uigetfile('*.txt','Select Metadata File');
metadataFileName = fullfile(param.rootDir,metadataFileName);

[ metadata, imageID, header, chanInfo ] = parseMetadataFile( metadataFileName );
numChannels=numel(chanInfo.channelNames);
% Select Output directories
rootOpDir =  uigetdir(pwd,'Select Output Directory');
opDir = (fullfile(rootOpDir,'SegmentedImages'));
opDirLabelled = (fullfile(rootOpDir,'LabelledImages'));
mkdir(opDir);mkdir(opDirLabelled);
% Select Channel for segmentation
[sel,~] = listdlg('ListString',chanInfo.channelNames,'SelectionMode','Single',...
                        'Name','Segmentation Channels','ListSize',[300 300]);
channelForSegmentation = chanInfo.channelNames{sel};
channelForSegmentation = strcmpi(channelForSegmentation,header);
wellCol = strcmpi('Well',header);
plateCol = strcmpi('Plate',header);
fieldCol = strcmpi('Field',header);
% treatmentCol = strcmpi('Treatment',header);
imID = strcmpi('ImageID',header);
stackCol = strcmpi('Stack',header);
uImageID = unique(imageID);


%% Core : Running segmentation & saving images
h = waitbar(0,'Writing Images');
for iImageID = 1:numel(uImageID)
    ii = imageID == uImageID(iImageID);
    [IM,focusIndex] = getfsimage(metadata(ii,channelForSegmentation));
    [~,L] = getSegmentedOverlayImage(IM,min_area_spheroid,radius_spheroid,smoothin_param,entropy_threshold,intensity_threshold,...
        scale_spheroid );
    uLabels = unique(L(:));
    xx = uLabels~=0;
    uLabels = uLabels(xx);
    numObjects = numel(uLabels);
    if(numObjects==0)
        disp('No Objects Found');
        continue;
    end

    ll = zeros(numObjects,2);
    for iObjects = 1:numObjects
        nL = L == uLabels(iObjects);
        ll(iObjects,:) = getFocusplanesPerObjectMod(nL,focusIndex,sum(ii));
    end
    fstruct = regionprops(L, IM, 'BoundingBox');
    fstruct = cell2mat(struct2cell(fstruct)');
    mData = metadata(ii,:);

    for iObjects = 1:numObjects
        for iPlanes = ll(iObjects,1):ll(iObjects,2)
            for kChannels = 1:numChannels
                IM1 = imread(mData{iPlanes,kChannels},'tif');
                IM2 = imcrop(IM1,fstruct(iObjects,:));

                opfileName = ['W' mData{1,wellCol} '__F'...
                    mData{1,fieldCol} '__CH' num2str(kChannels) '__Z'...
                    mData{iPlanes,stackCol} '__ID' num2str(uImageID(iImageID))...
                    '__OB' num2str(iObjects) '.tiff' ];
                imwrite(IM2,fullfile(opDir,opfileName),'tiff');
            end
        end
        opfileName = ['W' mData{1,wellCol} '__F'...
                    mData{1,fieldCol} '__CH' num2str(kChannels) '__Z1'...
                     '__ID' num2str(uImageID(iImageID))...
                    '__OB' num2str(iObjects) '.tiff' ];
        IML = imcrop(L==iObjects,fstruct(iObjects,:));
        imwrite(uint8(IML),fullfile(opDirLabelled,opfileName),'tiff');
    end
    if(numObjects>0)
%         re;
    end
    waitbar(iImageID./numel(uImageID),h,'Segmenting Organoids');
   
end
close(h);
msgbox('Operation Completed');