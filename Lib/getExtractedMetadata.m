function getExtractedMetadata(pth,str,exprIM,opFilename)

m = regexpi(str,exprIM,'Names');

if(isempty(m))
    errordlg('Regular Expression Mismatch');
    return;
end
fieldNameforStructure = fieldnames(m);
channelCol = find(strcmpi(fieldNameforStructure,'Channel'));
sizeHeader = numel(fieldnames(m));
%
% pth = 'D:\Projects\3dOncogenes\Images\Labelled2';
l = dir(pth);

mxRws = 100000;
metadata = cell(mxRws,sizeHeader+1);cnt = 1;
h = waitbar(0,'Extracting metadata');
% fprintf('Extracting metadata................');
for i = 3:size(l,1)
%     fprintf('\b\b\b\b\b\b\b\b%7.3f%%',i*100/size(l,1));
    waitbar(i/size(l,1),h);
    if(l(i).isdir)
        continue;
    end    
    t = regexpi(l(i).name,'.tif');
    if(isempty(t))
        continue;
    end
    m = regexpi(l(i).name,exprIM,'Names');
    if(~isempty(m))
        names = fieldnames(m);
        if(numel(names)~=sizeHeader)
            error('HHHHH');
        else
            metadata{cnt,1} = fullfile(pth,l(i).name);
            for j = 1:sizeHeader
                metadata{cnt,j+1} = getfield(m, names{j});
            end
            cnt = cnt+1;
        end
    end
end
close(h);
if(cnt <= mxRws)
    metadata = metadata(1:cnt-1,:);
end
numChannels = numel(unique(metadata(:,channelCol+1)));
uChannels = unique(metadata(:,channelCol+1));
% uChannels = str2num(char(uChannels));


%
[~,idx] = sort(metadata(:,channelCol+1));
metadata = metadata(idx,:);
allChl = reshape(metadata(:,1),size(metadata,1)/numChannels,numChannels);
% ii = str2num(char(metadata(:,channelCol+1))) == uChannels(1);
% Remove original Channel Column
origChannel = metadata(:,channelCol+1);
ii   = strcmpi(origChannel,uChannels(1));
removeColumnName = strcmpi(names,'Channel');
names = names(~removeColumnName);

metadata = metadata(:,[1:channelCol channelCol+2:end]);
nMetadata = [allChl metadata(ii,2:end)];


imId = getImageIDfromMetadata( nMetadata,pth,exprIM );
imId = num2cell(imId);

% Add metadata file column 
nMetadata  = [nMetadata repmat(cellstr(fullfile(pth,opFilename)),size(nMetadata,1),1)]; 
names = [names ;cellstr('MetadataFile')];

% Remove Additional Channel COlumn Name
% removeColumnName = strcmpi(names,'Channel');
% names = names(~removeColumnName);
% nMetadata = nMetadata(:,~removeColumnName);

header = cell(1,size(nMetadata,2));
for i = 1:numChannels
    header{1,i} = ['Channel_' uChannels{i}] ;
end
for i = numChannels+1:size(nMetadata,2)
    header(1,i) = names(i-numChannels);
end
% header = [header cellstr('MetadataFile')];
% Write Data


[m,n] = size(nMetadata);
fileName = fullfile(pth,opFilename);
try
    fid = fopen(fileName,'w');
    for i = 1:n
        fprintf(fid,'%s\t',header{1,i});
    end
    fprintf(fid,'%s\t','ImageID');
    fprintf(fid,'\n');
    
    h = waitbar(0,'Writing metadata');
    for i = 1:m
        for j = 1:n
            fprintf(fid,'%s\t',nMetadata{i,j});
        end
        fprintf(fid,'%f\t',imId{i,1});
        fprintf(fid,'\n');
        waitbar(i/m,h);
    end
    
    
    close(h);
%     fprintf(fid,'\n');
    
    fclose(fid);
catch expc
    fclose(fid);
    rethrow(expc);
end

msgbox('Metadata creation successful');

end