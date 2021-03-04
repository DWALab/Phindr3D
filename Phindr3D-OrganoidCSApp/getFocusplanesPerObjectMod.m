function [ll,n] = getFocusplanesPerObjectMod(labelImage,fIndex,numZ)
% getFocusplanesPerObject - Computes optimal focus plane  for  each object
% in a 3D stack
% labelImage - Boolean image indicating presence of an object
if(nargin == 2)
    numZ = max(fIndex(:));
%     SVSizeZ =3;
%     numZ2Remove =2;
elseif(nargin == 3)
%     SVSizeZ =3;
%     numZ2Remove =2;
end
% minZ = 1;
% maxZ = numZ;
% numObjects = max(labelImage(:));
% ll = zeros(numObjects,2);
try
ll = zeros(1,2);
% for iObjects = 1:numObjects
%     ii = labelImage==iObjects;
ii = fIndex(labelImage);
ii = ii(:);
% n = hist(ii,numZ+1);
n = histc(ii,[.5:1:numZ-.5]);
% n = n(2:end);
n = n./sum(n);
rndPoint = 1./(1*numZ);
p = find(n>rndPoint);
% If found nothing - 
if(isempty(p))
    minN = 1;
    maxN = numZ;
end
minN  = max(1,min(p)-2);
maxN = min(numZ,max(p)+2);

ll(1) = minN;
ll(2) = maxN;

catch expc
    rethrow(expc);
end
% end
end