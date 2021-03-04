function setChannelInformation(boxHandle,channelNames,channelColors,...
                                    selectedChannels)


channelNames = channelNames(selectedChannels);
channelColors = channelColors(selectedChannels',:);
str = cell(numel(channelNames),1);
for i = 1:size(channelColors,1)
    rgb = round(channelColors(i,:).*255);
    hex(:,2:7) = reshape(sprintf('%02X',rgb.'),6,[]).';
    hex(:,1) = '#';
%     data(i,2:4) = num2cell([param.maps(i,:)]);    
    str(i) = cellstr(['<html><font weight = "bold" size = 4 color="', ...
        hex, ...
        '">', ...
        channelNames{i}, ...
        '</font></html>']);
end

% str = [str '</BODY></HTML>'];
set(boxHandle,'String',str);
end