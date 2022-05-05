function [grps] = getGroupIndices(textData,grpNames,~)

if(nargin==3)
    output =1;
else
    output=0;
end
if(isempty(textData) || isempty(grpNames))
    disp('No Data');
    return;
end

numGrps = size(grpNames,1);
grps = zeros(size(textData,1),1);
for i = 1:numGrps
    p = strcmpi(grpNames(i),textData(:,1));
    idx = find(p);
    if(output)
        disp(sprintf('Number of Points in %s is %i',grpNames{i},numel(idx)));
    end
    if(isempty(idx))
        continue;
    end
%     cntrlData =[cntrlData ;Data.data(idx,:)];
    grps(idx,1) = i;
end
end