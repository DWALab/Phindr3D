function [L, N] = segmentImage(imfilename,minArea)

if(isstr(imfilename))
    I = imread(imfilename);
else
    I = imfilename;
end
% I = medfilt2(I);
imthreshold = getImageThreshold(double(I));
bw = bwareaopen(I>imthreshold, minArea,4);
% bw = bwmorph(bw,'majority',20);
[L, N] = bwlabel(bw, 8);
% allLbl = unique(L(:));
% subplot(2,1,1);imshow(L,[]);title('Before')
% Remove border objects

nI = false(size(I));
nI(:,[1 end]) = true;
nI([1 end],:) = true;
nL = L.*nI;
uL = unique(nL);

for i = 1:numel(uL)
    ii = L==uL(i);
    L(ii) = 0;
end
% subplot(2,1,2);imshow(L,[]);title('After');

% Measure Area for every Label
uL = unique(L);
% areaVal = zeros(numel(uL),1);
for i = 1:numel(uL)
    ii = L==uL(i);
    areaVal = sum(sum(ii));
    if(areaVal < minArea)
        L(ii) = 0;
    end
end
N = unique(L);
N = N(N>0);
% Rearraange L from 1
for i = 1:numel(N)
    ii = L==N(i);
    L(ii) = i;
end
N = unique(L);
N = sum(N>0);
% subplot(2,1,2);imshow(L,[]);title('After');
end