function setTextInformation(textHandle,imageFileName,channelNames,channelColors,...
                                    selectedChannels,projectionType)


channelNames = channelNames(selectedChannels);
channelColors = channelColors(selectedChannels',:);
str = ['File Name:: ' newline];
str = [str imageFileName{1,1} newline newline];
str = [str 'Projection Type :: ' projectionType newline newline];
% for i = 1:size(channelColors,1)
%     rgb = round(channelColors(i,:).*255);
%     hex(:,2:7) = reshape(sprintf('%02X',rgb.'),6,[]).';
%     hex(:,1) = '#';
% %     data(i,2:4) = num2cell([param.maps(i,:)]);    
%     str = ([str '<font color="', ...
%         hex, ...
%         '">', ...
%         channelNames{i}, ...
%         '</font></br>']);
% end

% str = [str '</BODY></HTML>'];
set(textHandle,'String',str);
end