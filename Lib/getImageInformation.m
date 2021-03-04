function [ d,fmt ] = getImageInformation( fileNames )
%getImageDimensions Gets image dimensions from file names

if(isempty(fileNames))
    error('@getImageInformation: File name empty');
end
d = ones(1,3);fmt = 'tif';
imFileName = unique(fileNames(:,1));
imFileName = imFileName{1,1}; 
d(1,3) = size(fileNames,1);
info = imfinfo(imFileName);
d(1,1) = info.Height;
d(1,2) = info.Width;
fmt = info.Format;

end

