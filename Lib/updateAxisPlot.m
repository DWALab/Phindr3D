function  updateAxisPlot(data,groupValues,colorValues,axisHandle)

% Function Description


% End Function Description


n = size(data,2);

if(n>3 || n <2)
    errordlg('@Plotting error - Undefined dimesions');
    return;
end
[az, el] = view(axisHandle);
if(~isempty(groupValues))
    uniqueGroups = unique(groupValues);
    for i = 1:numel(uniqueGroups)
        ii = strcmpi(uniqueGroups{i},groupValues);
        if(n==3)
            h = plot3(data(ii,1),data(ii,2),data(ii,3),'o','Markersize',5,...
                'MarkerEdgeColor','none','MarkerFaceColor',colorValues(i,:),'Parent',axisHandle);
        else
            h = plot(data(ii,1),data(ii,2),'o','Markersize',5,...
                'MarkerEdgeColor','none','MarkerFaceColor',colorValues(i,:),'Parent',axisHandle);
        end
        set(h,'hittest','off');
        if(i == 1)
            hold(axisHandle,'on');
        end
    end
    hold(axisHandle,'off');
    legend(uniqueGroups);
else
    if(n==3)
        h = plot3(data(:,1),data(:,2),data(:,3),'o','Markersize',4,...
            'MarkerEdgeColor','none','MarkerFaceColor',colorValues(1,:),'Parent',axisHandle);
    else
        h = plot(data(:,1),data(:,2),'o','Markersize',4,...
            'MarkerEdgeColor','none','MarkerFaceColor',colorValues(1,:),'Parent',axisHandle);
    end    
    set(h,'hittest','off');
end

set(axisHandle,'Visible','on');
set(axisHandle,'XTickLabel',[]);
set(axisHandle,'YTickLabel',[]);
set(axisHandle,'ZTickLabel',[]);
view(axisHandle,[az el]);
end