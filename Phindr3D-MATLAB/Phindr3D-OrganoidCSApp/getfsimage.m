function [finalImage, focusIndex] = getfsimage(fnames,showWBar)
% getfsimage - Outputs bets focussed image from a set of 3D image slices
% Input:
% fnames - 3D image file names
% Output:
% final_image: Best focussed image
% **********Edited March 31 2017*************
% ***********Santosh Hariharan***********
if(nargin==1)
    showWBar = false;
end

imInfo = imfinfo(fnames{1,:},'tiff');
% binsize = 1;
% m = m/binsize;n = n/binsize;
% clear IM1;
numZ = size(fnames,1);
% k_size = 5;
kernel = ones(5);
% fIM = zeros(m*n,numZ);
% fgIM = zeros(m*n,numZ);
prevImage = -inf(imInfo.Height,imInfo.Width);
focusIndex = zeros(imInfo.Height,imInfo.Width);
finalImage = zeros(imInfo.Height,imInfo.Width);
if(showWBar)
    h1 = waitbar(0,'Computing focus stack.....','Name','Focus stack');
end
tic;
for iFiles = 1:numZ    
    IM = double(imread(fnames{iFiles,:},'tiff'));
%     imshow(IM,[]);
    set(gca,'Visible','Off');
%     IM = medfilt2(IM);   
    tmp = imgradient(stdfilt((IM),kernel));
%     tmp = imgradient(medfilt2(IM));
    ii = tmp >= prevImage;
    focusIndex(ii) = iFiles;
    finalImage(ii) = IM(ii);
%     fIM(:,i) = reshape(IM,m*n,1);
%     fgIM(:,i) = reshape(imgradient(stdfilt(IM,ones(k_size))),m*n,1);
    prevImage = max(tmp,prevImage);
%     prevImage(ii) = tmp(ii);
    if(showWBar)
        waitbar(iFiles/numZ,h1);
    end
end
if(showWBar)
    close(h1);
end
fprintf('Time for focus computation %fs\n',toc);


end


function im = binImage(I,bsize)

[m,n] = size(I);
B1 = im2col(I,[bsize bsize],'distinct');
B1 = mean(B1);
im = reshape(B1,m/bsize,n/bsize);
end

