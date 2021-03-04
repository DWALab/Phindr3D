function setImageView(imageFileNames,channelColorValue,selectedViewType,selectedChannels,axisHandle)


imageFileNames = imageFileNames(:,selectedChannels);
channelColorValue = channelColorValue(selectedChannels',:);
imageInfo = imfinfo(imageFileNames{1,1});
[m,n] = size(imageFileNames);
if(m==1)
    selectedViewType = 'Slice';
end
% image2Show = zeros(imageInfo.Height,imageInfo.Width,sum(selectedChannels),size(imageFileNames,1));
if(strcmpi(selectedViewType,'MIP') || strcmpi(selectedViewType,'Slice'))
    image2Show = zeros(imageInfo.Height,imageInfo.Width,sum(selectedChannels));
    for i = 1:n
        image2Show(:,:,i) = getMIPImage( imageFileNames(:,i) );
    end
    image2Show = mergeChannels(image2Show,channelColorValue);
    h = imshow(image2Show,'Parent',axisHandle);
elseif(strcmpi(selectedViewType,'Montage'))
    image2Show = zeros(imageInfo.Height,imageInfo.Width,3,size(imageFileNames,1));
    for i = 1:m
        imtmp = zeros(imageInfo.Height,imageInfo.Width,sum(selectedChannels));
        for j = 1:n
            imtmp(:,:,j) = imread(imageFileNames{i,j},imageInfo.Format);
        end
        image2Show(:,:,:,i) = mergeChannels(imtmp,channelColorValue);
    end
    h = montage(image2Show,'Parent',axisHandle);    
end
set(h,'hittest','off');
set(axisHandle,'Visible','on');
set(axisHandle,'XTickLabel',[]);
set(axisHandle,'YTickLabel',[]);

