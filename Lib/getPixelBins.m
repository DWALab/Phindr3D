function [ binCenters ] = getPixelBins( x,numBins)
%getPixelBins Get pixel centers from training images
% For each voxel, assign categories
% Inputs
% x - m x n (m is the number of observations and n could be number of channels or category fractions)
% numBins - Number of categories
% Outputs
% binCenters - (numBins+1) x n (The first centroid are zeros- indicating background)

% numBins = param.numVoxelBins;
% Use kmeans clustering to get 
[m,~] = size(x);
if(m>50000)
    samSize = 50000;
else
    samSize = m;
end
% fprintf('@getPixelBins')    
if(m>samSize)
    numRandRpt = 10;
    binCenters = zeros(numBins,size(x,2),numRandRpt);
    sumD = zeros(numRandRpt,1);
    for iRandCycle = 1:numRandRpt
        [~,binCenters(:,:,iRandCycle)] = kmeans(x(randperm(m,samSize),:),...
                                        numBins,'replicates',100,'emptyaction','singleton',...
                                        'options',statset('Maxiter',100),'onlinephase','off');
        a = bsxfun(@plus,dot(binCenters(:,:,numRandRpt),binCenters(:,:,numRandRpt),2)',dot(x,x,2)) -2*(x*binCenters(:,:,numRandRpt)');
        sumD(iRandCycle) = sum(min(a,[],2));
    end
    
    [~, minDis] = min(sumD);
    binCenters = binCenters(:,:,minDis);
else
    [~,binCenters] = kmeans(x(:,:),numBins,'replicates',100,'emptyaction','singleton');
end    
%     binCenters = [zeros(1,size(x,2));binCenters];% Include background centroid 
end

