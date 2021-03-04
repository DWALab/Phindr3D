function im3D = getMerged3DImage(filenames,colors,boundValues,thresholdValues)
% numSlice = size(filenames,1);
% colors = param.channelCol;
% if(nargin==3)
%     gammaVal = 1*ones(1,size(colors,1));
% end
if(iscell(filenames))
    if(size(filenames,2) ~= size(colors,1))
        im3D = ones(1000,1000,3);
        return;
    end
    numChannels = size(filenames,2);
    info = imfinfo(filenames{1,1});    
    imWidth = info.Width;
    imHeight = info.Height;
    cellFile = 1;
else
    if(size(filenames,3) ~= size(colors,1))
        im3D = ones(1000,1000,3);
        return;
    end
    numChannels = size(filenames,3);
    imWidth = size(filenames,2);
    imHeight = size(filenames,1);
    cellFile = 0;
end

im3D = zeros(imHeight,imWidth,3);
% Assign pseudocolors to image

for jChannel = 1:numChannels
    %     for iSlice = 1:numSlice
    if(cellFile)
        im = double(imread(filenames{1,jChannel}));
    else
        im = filenames(:,:,jChannel);
    end
%     im = (im - min(im(:)))./(max(im(:)) - min(im(:)));
    maxMin = abs(boundValues(jChannel,2) - boundValues(jChannel,1));
    im = (im - boundValues(jChannel,1))./maxMin;
    im(im>1) = 1;
    im(im<0) = 0;
    im = im.*(im >= thresholdValues(jChannel)); 
%     im = imadjust(im,[],[],gammaVal(jChannel));
%     im = repmat(im,[1 1 3]);
%     colors(jChannel,:) = colors(jChannel,:)/3;
    im3D(:,:,1) = im3D(:,:,1) + colors(jChannel,1).*im;
    im3D(:,:,2) = im3D(:,:,2) + colors(jChannel,2).*im;
    im3D(:,:,3) = im3D(:,:,3) + colors(jChannel,3).*im;
    %     end
end
% den =sum(im3D(:,:,3).^2,3);
% den = sqrt(den);
% im3D = im3D./repmat(den,[1 1 3]);
for i = 1:3
    maxI = max(max(im3D(:,:,i)));
    minI = min(min(im3D(:,:,i)));
    if((maxI - minI)>0)
        im3D(:,:,i) = (im3D(:,:,i) - minI)./ (maxI - minI);
    end
end
% im3D = imadjust(im3D,[],[],[1 1 .6]);
end

