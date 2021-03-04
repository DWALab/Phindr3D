function [ mData, imageID, header, chanInfo ] = parseMetadataFile( metadatafilename )
%parseMetadataFile Parses metadata file 
%   Author: Santosh hariharan @ DWA Lab Toronto
% Date oct 4 2017
mData = {};chanInfo={};header = {};
imageID = [];
try
    fid = fopen(metadatafilename,'r');
    header= strtrim(fgetl(fid));
    fclose(fid);
    header = regexpi((header),'\t','split');
    if(~strcmpi(header,'ImageID'))
        errordlg('Please choose appropriate metadata file');
        return;
    end
    fid = fopen(metadatafilename);
    tmp = textscan(fid,repmat('%s',1,numel(header)),'headerlines',1,'delimiter','\t');
    fclose(fid);    
catch excep
    fclose(fid);
    rethrow(excep);
end

for i = 1:size(tmp,2)
    mData = [mData tmp{1,i}];
end

[chanInfo.channelColNumber,~] = listdlg('ListString',header,'SelectionMode','Multiple',...
                        'Name','Select Channels','ListSize',[300 300]);
chanInfo.channelNames = header(1,chanInfo.channelColNumber);
chanInfo.channelColors = lines(numel(chanInfo.channelColNumber));
ii = strcmpi(header,'ImageID');
imageID = str2num(char(mData(:,ii)));
stackCol = or(strcmpi(header,'Stack'),strcmpi(header,'Stacks'));
uImageID = unique(imageID);
h = waitbar(0,'Extracting Image Id');
for i = 1:numel(uImageID)
    ii = imageID == uImageID(i);
    kk = str2num(char(mData(ii,stackCol)));
    tmp = mData(ii,:);
    [~,kk] = sort(kk,'ascend');
    mData(ii,:) = tmp(kk,:);
    waitbar(i/numel(uImageID),h);
end
close(h);
ii = strcmpi(header,'ImageID');
imageID = str2num(char(mData(:,ii)));
end

