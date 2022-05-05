function [clusterResult] = computeClustering(data,numberClusters,type)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

if(nargin==2)
    type = 'AP';
end
h = waitbar(0,'Clustering.......');
[C] =  clsIn(data);
waitbar(0.5,h,'Clustering.......');
if(strcmpi(type,'AP'))    
    clusterResult = apclusterK(C.S,numberClusters);
    waitbar(1,h,'Clustering.......');   
else
    clusterResult = [1:size(data,1)]';
end
close(h);
end

