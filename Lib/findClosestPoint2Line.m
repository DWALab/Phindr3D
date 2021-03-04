function [closestIndex]  = findClosestPoint2Line(pts,v1,v2)
d = zeros(size(pts,1),1);
if(size(pts,2) == 2)
    pts = [pts zeros(size(pts,1),1)];
end
for i = 1:size(pts,1)
    d(i) = getDistancePointFromLine(pts(i,:), v1, v2);
end
[~,closestIndex]  =min(d);
end