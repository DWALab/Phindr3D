function [ pieFigHandle ] = viewScatterPie2(x,y,yhat,map,uY,uYhat)
%viewScatterPie Plots data in x using grouping in y with colours of yhat
% 
% 

if(size(x,2)>2)
    error('@viewScatterPie: Only two dmensional plot allowed');    
end

if(size(y,1)~=size(yhat,1))
    error('@viewScatterPie: y and yhat must be of same length');
end

% figure;plot(x(:,1),x(:,2),'o');
% if(size(map,1) ~= numel(uYhat))
% %     map = jet(numel(uYhat)); % Default Color map
% end
if(nargin==4)
uY = unique(y);
    uYhat = unique(yhat);
end

if(nargin==5)
    uYhat = unique(yhat);
end
% Compute distribution matrix
disMat = zeros(numel(uYhat),numel(uY));
for iTreatments = 1:numel(uYhat)
    ii = strcmpi(uYhat{iTreatments,:},yhat);
    for jClusters = 1:numel(uY)
        jj = y==uY(jClusters);
        disMat(iTreatments,jClusters) = sum(ii.*jj);
    end
end

rsize = sum(disMat,1);
% rsize = rsize./sum(rsize);

axisRange = abs(max(x)-min(x));
maxRadius = .06*min(axisRange);
minRadius = .03*min(axisRange);

% scalingFact = 5;
% rsize = rsize*scalingFact;
rsize = sum(disMat,1);
rsize = (rsize - min(rsize))./(max(rsize)- min(rsize));
rsize = (maxRadius - minRadius)*rsize + minRadius;
% First plot clusters with lines from centroid of each cluster

pieFigHandle = figure;
hold on;

plot(x(:,1),x(:,2),'o',...
        'MarkerSize',4,'MarkerEdgeColor','none',...
        'MarkerFaceColor',[.6 .6 .6]);
for iClusters = 1:numel(uY)
    ii = y == uY(iClusters);
     cCenter = repmat(x(uY(iClusters),:),sum(ii),1);
    x1 = [cCenter(:,1) x(ii,1)];
    y1 = [cCenter(:,2) x(ii,2)];
    line(x1',y1','Color',[.6 .6 .6],'MarkerSize',3,'MarkerEdgeColor','none',...
        'MarkerFaceColor',[.6 .6 .6]);

   
    
end

% xticklabels({});yticklabels({});set(gca,'xtick',[]);set(gca,'ytick',[]);

% hold off;
%
% In the same figure plot data using patches - Uses inbuilt Matlab function
% logic
% 
% numSmallPatch = 30;
numTreatments = size(disMat,1);
% angleStart = 0;
numSteps = 30;
% rsize = 5;
% hold on;
viscircles(x(uY,:),rsize,'Linewidth',1,'LineStyle','-','Color',[0 0 0]);
for iClusters = 1:numel(uY)
    startAngle = 0;  
    treatProportion = disMat(:,iClusters)./sum(disMat(:,iClusters));
    cCenter = x(uY(iClusters),:);
    hall=[];
    for jTreatment =  1:numTreatments
        step = treatProportion(jTreatment)*2*pi/numSteps;
        theta = [0 0:step:treatProportion(jTreatment)*2*pi 0];
        theta = theta + startAngle;
        [x1, y1] = pol2cart(theta,[0 rsize(iClusters).*(ones(1,numel(theta)-2)) 0]);
        x1 = x1 + cCenter(1,1);
        y1 = y1 + cCenter(1,2);
        h1 = patch(x1,y1,jTreatment,'FaceColor',map(jTreatment,:),'EdgeColor','none','FaceVertexAlphaData',1);
        hall = [hall;h1];
        startAngle = max(theta);  
       
    end    
%     legend(uYhat)
end

% set(gca,'children',flipud(get(gca,'children')))
% if(textOnPlot)
    for iClusters = 1:numel(uY)
        text(x(uY(iClusters),1),x(uY(iClusters),2),[num2str(iClusters)],'FontWeight','bold',...
            'Color',[1 1 1]) ;
    end
% end
hold off;axis equal
xticklabels({});yticklabels({});set(gca,'xtick',[]);set(gca,'ytick',[]);
% set(gca,'children',flipud(get(gca,'children')))
% legend(hall,uYhat);
% clear hall

end

