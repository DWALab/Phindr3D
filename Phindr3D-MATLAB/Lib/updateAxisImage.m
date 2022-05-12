function updateAxisImage(axisHandle,image2Display,typeOfView)
% updateAxisImage(axisHandle,image2Display,typeOfView) 
%   Updates image to be displayed in the axis defined by handle
%
% Input parameters
%
% axisHandle - Handle of the axes object where image is displayed
%
% image2Display - Image to be displayed. 
%
% typeOfView - Montage, MIP. Any other choice defaults to single plane
% ---------------------------------------
% Created: Santosh Hariharan 
% Date: Aug 13 2018
% DWA Lab, University Of Toronto
% ---------------------------------------

if(strcmpi(typeOfView,'montage'))
    h = montage(image2Display,'Parent',axisHandle);    
elseif(strcmpi(typeOfView,'MIP'))    
    h = imshow(image2Display,[],'Parent',axisHandle);
else
    h = imshow(image2Display,[],'Parent',axisHandle);    
end

set(h,'hittest','off');
set(axisHandle,'Visible','on');
set(axisHandle,'XTick',[]);
set(axisHandle,'YTick',[]);

end

