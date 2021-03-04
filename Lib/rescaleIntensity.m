function [ im ] = rescaleIntensity( im ,low,high)
%rescaleIntensity Rescales intensity of the image based on the lower and
%upper bounds
%   
if(nargin ==1)
    low = 0;
    high = 1;
end
im = double(im);
% minIM = min(im(:));
% maxIM = max(im(:));
diffIM = high-low;
im = (im - low)/diffIM;
im(im>1) = 1;
im(im<0) = 0;
end

