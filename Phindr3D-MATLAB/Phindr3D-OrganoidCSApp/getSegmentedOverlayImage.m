function [seg_image,L] = getSegmentedOverlayImage(final_im,min_area_spheroid,radius_spheroid,...
smoothin_param,entropy_thresh,intensity_threshold,scale_spheroid )

newfim = final_im;
SE = strel('disk',2*radius_spheroid);
IM2 = imtophat(newfim,SE);
IM4 = smoothImage(IM2,smoothin_param);
minIM = min(IM4(:));
maxIM = max(IM4(:));
IM4 = (IM4 - minIM);
IM4 = IM4./(maxIM - minIM);
IM4 = imadjust(IM4,[],[],.5);
% March 3 2017 - Added following code
[ IM6 ] = segmentImage( IM4,min_area_spheroid );
IM6 = IM6>0;
IM6 = bwmorph(IM6,'close',3);
IM6 = imfill(IM6,8,'holes');
IM6 = bwareaopen(IM6,20);
IM7 = bwdist(~IM6);
if(scale_spheroid>1)
    scale_spheroid = 1;
elseif(scale_spheroid<=0)
    scale_spheroid = .1;
end
splitFactor = scale_spheroid.*radius_spheroid;
IM9 = imextendedmax(IM7,splitFactor);
bw = ~IM6 | IM9;
IM10 = imimposemin(imcomplement(IM4.*IM7),bw);
L = watershed(IM10);
L = max(L-1,0);

% Remove objects touching the border
L = removeBorderObjects(L,10);
[IM11] = (final_im - min(final_im(:)))/(max(final_im(:)) - min(final_im(:)));
rr(:,1) = struct2cell(regionprops(L,'Area'));
rr(:,2) = struct2cell(regionprops(L,final_im,'MeanIntensity'));
rr(:,3) = struct2cell(regionprops(L,entropyfilt(IM11,true(5)),'MeanIntensity'));
rr = cell2mat(rr);
% assignin('base','rr',rr);
if(~isempty(rr))
    i2 = rr(:,1) >= min_area_spheroid;
    i3 = rr(:,2) >= intensity_threshold;
    i4 = rr(:,3) >= entropy_thresh;
    ii = find(i2.*i3.*i4 ==0); % ii contains labels to be removed
    for i = 1:numel(ii)
        L(L==ii(i)) = 0;
    end
end
L = resetLabelImage(L);
seg_image = bwperim(L>=1);
seg_image = bwmorph(seg_image,'dilate',1);

end
