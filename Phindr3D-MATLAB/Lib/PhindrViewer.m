function varargout = PhindrViewer(varargin)
% PHINDRVIEWER MATLAB code for PhindrViewer.fig
%      PHINDRVIEWER, by itself, creates a new PHINDRVIEWER or raises the existing
%      singleton*.
%
%      H = PHINDRVIEWER returns the handle to a new PHINDRVIEWER or the handle to
%      the existing singleton*.
%
%      PHINDRVIEWER('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in PHINDRVIEWER.M with the given input arguments.
%
%      PHINDRVIEWER('Property','Value',...) creates a new PHINDRVIEWER or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before PhindrViewer_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to PhindrViewer_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help PhindrViewer

% Last Modified by GUIDE v2.5 29-Jul-2018 15:31:52

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @PhindrViewer_OpeningFcn, ...
                   'gui_OutputFcn',  @PhindrViewer_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before PhindrViewer is made visible.
function PhindrViewer_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to PhindrViewer (see VARARGIN)

% Choose default command line output for PhindrViewer
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);
set(handles.plotAxes,'XTickLabel',[]);
set(handles.plotAxes,'YTickLabel',[]);
set(handles.plotAxes,'ZTickLabel',[]);
set(0, 'DefaultFigureRenderer', 'painters');

% UIWAIT makes PhindrViewer wait for user response (see UIRESUME)
% uiwait(handles.PhindrViewer);


% --- Outputs from this function are returned to the command line.
function varargout = PhindrViewer_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on selection change in plotType.
function plotType_Callback(hObject, eventdata, handles)
% hObject    handle to plotType (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns plotType contents as cell array
%        contents{get(hObject,'Value')} returns selected item from plotType
pltType = get(hObject,'String');
pltType = pltType{get(hObject,'Value')};

cMap = getappdata(handles.PhindrViewer,'cMap');% Color map
data = getappdata(handles.PhindrViewer,'data');% data

selectedMetadataColumnVal = get(handles.columnColor,'Value');
selectedMetadataColumn = get(handles.columnColor,'String');
selectedMetadataColumn = selectedMetadataColumn{selectedMetadataColumnVal};


txtData = getappdata(handles.PhindrViewer,'txtData');
txtHeader = getappdata(handles.PhindrViewer,'txtHeader');
% projectedData = getappdata(handles.PhindrViewer,'projectedData');
selectedMetadataColumn = strcmpi(txtHeader,selectedMetadataColumn);

if(sum(selectedMetadataColumn)~=0)
    selectedMetadataColumnValues = txtData(:,selectedMetadataColumn);  
else
    selectedMetadataColumnValues = [];
    cMap = [0 0 1];
end

if(get(handles.plot3D,'Value'))
    projectedData = compute_mapping(data,pltType,3);
%     scatter(projectedData(:,1),projectedData(:,2),projectedData(:,3),10,cMap,'Parent',handles.plotAxes);
else
    projectedData = compute_mapping(data,pltType,2);
%     scatter(projectedData(:,1),projectedData(:,2),10,cMap,'Parent',handles.plotAxes);
end
updateAxisPlot(projectedData,selectedMetadataColumnValues,cMap,handles.plotAxes);
setappdata(handles.PhindrViewer,'projectedData',projectedData);



% --- Executes during object creation, after setting all properties.
function plotType_CreateFcn(hObject, eventdata, handles)
% hObject    handle to plotType (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in columnColor.
function columnColor_Callback(hObject, eventdata, handles)
% hObject    handle to columnColor (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns columnColor contents as cell array
%        contents{get(hObject,'Value')} returns selected item from columnColor
selectedMetadataColumnVal = get(hObject,'Value');
selectedMetadataColumn = get(hObject,'String');
selectedMetadataColumn = selectedMetadataColumn{selectedMetadataColumnVal};

txtData = getappdata(handles.PhindrViewer,'txtData');
txtHeader = getappdata(handles.PhindrViewer,'txtHeader');
projectedData = getappdata(handles.PhindrViewer,'projectedData');
selectedMetadataColumn = strcmpi(txtHeader,selectedMetadataColumn);

% Select Default Colormap
if(sum(selectedMetadataColumn)~=0)
    selectedMetadataColumnValues = txtData(:,selectedMetadataColumn);
    cMap = jet(numel(unique(selectedMetadataColumnValues)));    
else
    selectedMetadataColumnValues = [];
    cMap = [0 0 1];
end
updateAxisPlot(projectedData,selectedMetadataColumnValues,cMap,handles.plotAxes);
setappdata(handles.PhindrViewer,'cMap',cMap);

% --- Executes during object creation, after setting all properties.
function columnColor_CreateFcn(hObject, eventdata, handles)
% hObject    handle to columnColor (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in selectFeatureFile.
function selectFeatureFile_Callback(hObject, eventdata, handles)
% hObject    handle to selectFeatureFile (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
[extractedFeatureFilename, pth] = uigetfile('.txt','Import source file');
try
    fid = fopen(fullfile(pth,extractedFeatureFilename),'r'); % Read file
    header = regexp(strtrim(fgetl(fid)),'\t','split');  
    fclose(fid);
%     Check if imageid column exists
    if(~strcmpi(header,'imageid'))
        errordlg('Missing ImageID column!','File Error');
        return;
    end
    formatStr = repmat({'%f\t'},1,numel(header));
    textHeaderCol = false(1,numel(header)); 
    [selection,~] = listdlg('ListString',header,'SelectionMode','Multiple',...
                        'Name','Select Metadata','ListSize',[300 300]);
    formatStr(1,selection) = {'%s\t'};
    formatStr = sprintf('%s',formatStr{:});                
    fid = fopen(fullfile(pth,extractedFeatureFilename),'r');
    t = textscan(fid,formatStr,'Headerlines',1,'delimiter','\t');
    fclose(fid);
catch expc
    fclose(fid);
    rethrow(expc);
end

% Get Image ID's
imageID = t(1,strcmpi(header,'imageID'));
imageID = imageID{1};
imageID = str2num(char(imageID));

% Get metdata file name

metadataFileName = t(1,strcmpi(header,'metadataFile'));
if(isempty(metadataFileName))
    [FileName,PathName] = uigetfile('*.txt','Select Metadata File');
    metadataFileName = fullfile(PathName,FileName);
else
    metadataFileName = metadataFileName{1};
    metadataFileName = metadataFileName{1};
end


% Split Text & Data
textHeaderCol(1,selection) = true;
txtData = {};
for i = 1:numel(selection)
    txtData = [txtData t{1,selection(i)}];
end
data = cell2mat(t(1,~textHeaderCol));
txtHeader = header(1,textHeaderCol);
dataHeader = header(1,~textHeaderCol);
infRows = any(data == inf,2);
infRows = or(any(data == -inf,2),infRows);
infRows = or(any(isnan(data),2),infRows);
fprintf('Removed %i rows \n',sum(infRows));
data(infRows,:)=[];
txtData(infRows,:)=[];
[~,ix] = unique(data,'rows');
data = data(ix,:);
txtData = txtData(ix,:);



minD = min(data,[],1);
maxD = max(data,[],1);
data = bsxfun(@minus,data,minD);
data = bsxfun(@rdivide,data,maxD-minD);

% Remove columns with more than 80% NaN
ii = isnan(data);
ii = sum(ii,1);
ii = ii./size(data,1);
ii = ii <= .7;
data = data(:,ii);
fprintf('Removed %i Columns', sum(~ii));
% Extract Metadata -  To be used for image viewing

[ mData, metaImageID, metaHeader, chanInfo ] = parseMetadataFile( metadataFileName );


% Get channel Information
channelNames = chanInfo.channelNames;
channelColumns = false(1,numel(txtHeader));
for i = 1:numel(channelNames)
    channelColumns = or(channelColumns,strcmpi(channelNames{i},txtHeader));
end
txtData = txtData(:,~channelColumns);
txtHeader = txtHeader(1,~channelColumns);


% Read Metadatafile and get channel names & image Id's
channelColumns = false(1,numel(metaHeader));
for i = 1:numel(channelNames)
    channelColumns = or(channelColumns,strcmpi(channelNames{i},metaHeader));
end
channelColumns = mData(:,channelColumns);


%---- Set application data for main figure
setappdata(handles.PhindrViewer,'data',data);
setappdata(handles.PhindrViewer,'txtData',txtData);
setappdata(handles.PhindrViewer,'txtHeader',txtHeader);
setappdata(handles.PhindrViewer,'dataHeader',dataHeader);
setappdata(handles.PhindrViewer,'imageID',imageID);
setappdata(handles.PhindrViewer,'metadataFileName',metadataFileName);
setappdata(handles.PhindrViewer,'channelNames',channelNames);
setappdata(handles.PhindrViewer,'metaImageID',metaImageID);
setappdata(handles.PhindrViewer,'channelColumns',channelColumns);
setappdata(handles.PhindrViewer,'selectedMetadataColumn','');
set(handles.columnColor,'String',[cellstr('No Grouping') txtHeader]);


% Default Mapping
projectedData = compute_mapping(data,'PCA',2);
cMap = [0 0 1];
updateAxisPlot(projectedData,[],cMap,handles.plotAxes);
setappdata(handles.PhindrViewer,'projectedData',projectedData);
setappdata(handles.PhindrViewer,'cMap',cMap);

% --------------------------------------------------------------------
function da_Callback(hObject, eventdata, handles)
% hObject    handle to da (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function tmp_Callback(hObject, eventdata, handles)
% hObject    handle to tmp (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function clD_Callback(hObject, eventdata, handles)
% hObject    handle to clD (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function estimateCluster_Callback(hObject, eventdata, handles)
% hObject    handle to estimateCluster (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
exData = getappdata(handles.PhindrViewer,'data');
C = clsIn(exData);
step = 100;
pref = [C.pmin:(C.pmax - C.pmin)./step:C.pmax];
yCls = zeros(numel(pref),1);
h = waitbar(0,'Computing clusters..........');

for i = 1:numel(pref)
    idx = apcluster(C.S,pref(i),'dampfact',.9);
    uIdx = unique(idx);
    if((numel(uIdx) == numel(idx)) && i<numel(pref))
       if(i==1)
           yCls(i)=1;
       else
        yCls(i) = yCls(i-1);
       end
    else
        yCls(i) = numel(unique(idx));
    end
%     fprintf('\b\b\b\b\b\b\b\b%7.3f%%',i*100/step);
    waitbar(i/numel(pref),h);
end
close(h);
k = getBestPreference( pref',yCls,true );
msgbox(sprintf('Found %i Clusters. Please enter value in Manual Clustering Menu',k),'Cluster Estimation');


% --------------------------------------------------------------------
function manualCluster_Callback(hObject, eventdata, handles)
% hObject    handle to manualCluster (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

prompt = {'Select number of clusters & click OK for clustering:'};
numClusters = inputdlg(prompt,'Input number of clusters',1,{'7'});
if(isempty(numClusters))
    disp('No clusters selected');
    return;
end
data =getappdata(handles.PhindrViewer,'data');
% set(handles.PhindrViewer, 'pointer', 'watch')
numClusters = str2num(char(numClusters));
% Perform AP clustering Here
clusterResult = computeClustering(data,numClusters,'AP');
setappdata(handles.PhindrViewer,'clusterResult',clusterResult);
set(handles.pMap,'Enable','On');
set(handles.exportClusterResults,'Enable','On');
% set(handles.PhindrViewer, 'pointer', 'arrow');
msgbox('Completed Clustering');



% --------------------------------------------------------------------
function classificationTab_Callback(~, ~, handles)
% hObject    handle to classificationTab (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

data = getappdata(handles.PhindrViewer,'data');

selectedMetadataColumnVal = get(handles.columnColor,'Value');
selectedMetadataColumn = get(handles.columnColor,'String');
selectedMetadataColumn = selectedMetadataColumn{selectedMetadataColumnVal};

txtData = getappdata(handles.PhindrViewer,'txtData');
txtHeader = getappdata(handles.PhindrViewer,'txtHeader');
selectedMetadataColumn = strcmpi(txtHeader,selectedMetadataColumn);
% Select Default Colormap
if(sum(selectedMetadataColumn)~=0)
    selectedMetadataColumnValues = txtData(:,selectedMetadataColumn);        
else
    errordlg('Select Appropriate Grouping!','','modal');
end

uniqueSelectedMetadataColumnValues = unique(selectedMetadataColumnValues);
[selectControls,~] = listdlg('ListString',uniqueSelectedMetadataColumnValues,...
                            'SelectionMode','Multiple',...
                        'Name','Select Controls','ListSize',[300 300]);
if(numel(selectControls)<2)
    errordlg('Select at least 2 classes!','','modal');
    return;
end
controlValues = uniqueSelectedMetadataColumnValues(selectControls);
grpIndex = getGroupIndices(selectedMetadataColumnValues,controlValues);
groupPartition = equalTrainingSamplePartition(grpIndex,floor(.6*(sum(grpIndex>0)/numel(controlValues))));
% Classify Data 
% --Create model
h = waitbar(.4,'Building classifier..');
classificationModel = TreeBagger(500,data(groupPartition.training,:),...
                            selectedMetadataColumnValues(groupPartition.training,1));
% --Predict Unknowns
waitbar(.7,h,'Predicting Unknowns..');
[Yfit,~,~] = predict(classificationModel,data(or(groupPartition.test,grpIndex==0),:));
outputColumn = selectedMetadataColumnValues(or(groupPartition.test,grpIndex==0),1);
% Display Results %%
%  -- Reformat Table
classificationTable = zeros(numel(uniqueSelectedMetadataColumnValues),numel(controlValues));
for i = 1:numel(uniqueSelectedMetadataColumnValues)
    ii = strcmpi(outputColumn,uniqueSelectedMetadataColumnValues{i});
    for j = 1:numel(controlValues)
        jj = strcmpi(Yfit,controlValues{j});
        classificationTable(i,j) = sum(ii.*jj);
    end
end
% Export Classification Result %%
[fileName,PathName,~] = uiputfile('*.txt','Save Classification Output');
fileName = fullfile(PathName,fileName);
waitbar(.9,h,'Writing output to file..');
try
    fid = fopen(fileName,'w');
%     Write header
    fprintf(fid,'%s\t','');
    for i = 1:numel(controlValues)
        fprintf(fid,'%s\t',controlValues{i});
    end
    fprintf(fid,'\n');
    for i = 1:numel(uniqueSelectedMetadataColumnValues)
        fprintf(fid,'%s\t',uniqueSelectedMetadataColumnValues{i});
        for j = 1:numel(controlValues)
            fprintf(fid,'%f\t',classificationTable(i,j));
        end
        fprintf(fid,'\n');
    end
    fclose(fid);
catch expc
    fclose(fid);
    rethrow(expc);
end
waitbar(1,h,'Writing output to file..');
close(h);


% --------------------------------------------------------------------
function Untitled_1_Callback(~, ~, ~)
% hObject    handle to Untitled_1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function Untitled_2_Callback(~, ~, ~)
% hObject    handle to Untitled_2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function showImageforData_Callback(~, ~, handles)
% hObject    handle to showImageforData (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get Closest Point

cMap = getappdata(handles.PhindrViewer,'cMap');
selectedMetadataColumnVal = get(handles.columnColor,'Value');
selectedMetadataColumn = get(handles.columnColor,'String');
selectedMetadataColumn = selectedMetadataColumn{selectedMetadataColumnVal};

txtData = getappdata(handles.PhindrViewer,'txtData');
txtHeader = getappdata(handles.PhindrViewer,'txtHeader');
projectedData = getappdata(handles.PhindrViewer,'projectedData');
selectedMetadataColumn = strcmpi(txtHeader,selectedMetadataColumn);

% Select Default Colormap
if(sum(selectedMetadataColumn)~=0)
    selectedMetadataColumnValues = txtData(:,selectedMetadataColumn);        
else
    selectedMetadataColumnValues = [];
    cMap = [0 0 1];
end
n = size(projectedData,2);
pointClicked=get(handles.plotAxes,'CurrentPoint');

I  = findClosestPoint2Line(projectedData,pointClicked(1,:),pointClicked(2,:));

hold(handles.plotAxes,'on');
if(n==3)
    h = plot3(projectedData(I,1),projectedData(I,2),projectedData(I,3),'o','Markersize',7,...
        'MarkerEdgeColor',[.5 .5 .5],'MarkerFaceColor','none','Parent',handles.plotAxes);
else
    h = plot(projectedData(I,1),projectedData(I,2),'o','Markersize',7,...
        'MarkerEdgeColor',[.5 .5 .5],'MarkerFaceColor','none','Parent',handles.plotAxes);
end
updateAxisPlot(projectedData,selectedMetadataColumnValues,cMap,handles.plotAxes);
hold(handles.plotAxes,'off');
set(h,'hittest','off');
set(handles.plotAxes,'Visible','on');

imageID = getappdata(handles.PhindrViewer,'imageID');
channelNames = getappdata(handles.PhindrViewer,'channelNames');
metaImageID = getappdata(handles.PhindrViewer,'metaImageID');
channelColumns = getappdata(handles.PhindrViewer,'channelColumns');
ii = metaImageID == imageID(I);
if(~isappdata(0,'channelColorValue'))
    setappdata(0,'channelColorValue',lines(numel(channelNames)));
end
imageViewer(channelColumns(ii,:),channelNames);


% --------------------------------------------------------------------
function exportPlot_Callback(~, ~, handles)
% hObject    handle to exportPlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

h = figure;
h1 = copyobj(handles.plotAxes, h);
set(h1, 'Units', 'normalized', 'Position', [.1 .1 .8 .8]);
filterSpec = {'*.fig';'*.jpg';'*.png';'*.bmp';'*.svg';'*.*'};
[fileName,pathName] = uiputfile(filterSpec);

saveas(h1,fullfile(pathName,fileName));
% --------------------------------------------------------------------
function plotClick_Callback(~, ~, ~)
% hObject    handle to plotClick (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function Untitled_3_Callback(~, ~, ~)
% hObject    handle to Untitled_3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function classificationParameters_Callback(~, ~, ~)
% hObject    handle to classificationParameters (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function importSession_Callback(~, ~, ~)
% hObject    handle to selectFeatureFile (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function exportSession_Callback(~, ~, ~)
% hObject    handle to exportSession (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes when selected object is changed in plotDimensions.
function plotDimensions_SelectionChangedFcn(~, ~, handles)
% hObject    handle to the selected object in plotDimensions 
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
pltType = get(handles.plotType,'String');
pltType = pltType{get(handles.plotType,'Value')};

data = getappdata(handles.PhindrViewer,'data');% Data
cMap = getappdata(handles.PhindrViewer,'cMap');% Colors

selectedMetadataColumnVal = get(handles.columnColor,'Value');
selectedMetadataColumn = get(handles.columnColor,'String');
selectedMetadataColumn = selectedMetadataColumn{selectedMetadataColumnVal};

txtData = getappdata(handles.PhindrViewer,'txtData');
txtHeader = getappdata(handles.PhindrViewer,'txtHeader');

selectedMetadataColumn = strcmpi(txtHeader,selectedMetadataColumn);

% Select Default Colormap
if(sum(selectedMetadataColumn)~=0)
    selectedMetadataColumnValues = txtData(:,selectedMetadataColumn);  
else
    selectedMetadataColumnValues = [];
end

if(get(handles.plot3D,'Value'))
    projectedData = compute_mapping(data,pltType,3);
    set(handles.pMap,'Enable','Off');

else
    projectedData = compute_mapping(data,pltType,2);
    set(handles.pMap,'Enable','On');
end

updateAxisPlot(projectedData,selectedMetadataColumnValues,cMap,handles.plotAxes);


% legend(selectedMetadataValues);
setappdata(handles.PhindrViewer,'projectedData',projectedData);


% --------------------------------------------------------------------
function setPlotColors_Callback(~, ~, handles)
% hObject    handle to setPlotColors (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% get(handles.plotAxes,'CurrentPoint')
cMap = getappdata(handles.PhindrViewer,'cMap');
projectedData = getappdata(handles.PhindrViewer,'projectedData');
selectedMetadataColumnVal = get(handles.columnColor,'Value');
selectedMetadataColumn = get(handles.columnColor,'String');
selectedMetadataColumn = selectedMetadataColumn{selectedMetadataColumnVal};

txtData = getappdata(handles.PhindrViewer,'txtData');
txtHeader = getappdata(handles.PhindrViewer,'txtHeader');
selectedMetadataColumn = strcmpi(txtHeader,selectedMetadataColumn);

% Select Default Colormap
if(sum(selectedMetadataColumn)==0)
    selectedMetadataColumnValues = [];
else    
    selectedMetadataColumnValues = txtData(:,selectedMetadataColumn);    
end
[cMap] = colorpicker(unique(selectedMetadataColumnValues),cMap);
setappdata(handles.PhindrViewer,'cMap',cMap);
updateAxisPlot(projectedData,selectedMetadataColumnValues,cMap,handles.plotAxes);


% --------------------------------------------------------------------
function Untitled_4_Callback(~, ~, ~)
% hObject    handle to Untitled_4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function rotatePlot_Callback(hObject, ~, handles)
% hObject    handle to rotatePlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if(strcmpi(get(hObject,'Checked'),'On'))
    rotate3d(handles.plotAxes,'Off');
    set(hObject,'Checked','Off');
else
    rotate3d(handles.plotAxes,'On');
    set(hObject,'Checked','On');
end

% --------------------------------------------------------------------
function rotateOn_Callback(~, ~, ~)
% hObject    handle to rotateOn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function pMap_Callback(~, ~, handles)
% hObject    handle to pMap (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if(isappdata(handles.PhindrViewer,'clusterResult'))
    clusterResult = getappdata(handles.PhindrViewer,'clusterResult');
else
    errordlg('No clustering data found!','','modal');
    return;
end
cMap = getappdata(handles.PhindrViewer,'cMap');
projectedData = getappdata(handles.PhindrViewer,'projectedData');
if(size(projectedData,2)>2)
    errordlg('Pie Maps only for 2D plots','','modal');
    return;
end
selectedMetadataColumnVal = get(handles.columnColor,'Value');
selectedMetadataColumn = get(handles.columnColor,'String');
selectedMetadataColumn = selectedMetadataColumn{selectedMetadataColumnVal};

txtData = getappdata(handles.PhindrViewer,'txtData');
txtHeader = getappdata(handles.PhindrViewer,'txtHeader');
selectedMetadataColumn = strcmpi(txtHeader,selectedMetadataColumn);

% Select Default Colormap
if(sum(selectedMetadataColumn)==0)
    selectedMetadataColumnValues = [];
else    
    selectedMetadataColumnValues = txtData(:,selectedMetadataColumn);    
end
clusterPieFigureHandle = viewScatterPie2(projectedData,clusterResult,selectedMetadataColumnValues,cMap);
% set(clusterPieFigureHandle, 'Units', 'normalized', 'Position', [.1 .1 .8 .8]);
filterSpec = {'*.fig';'*.jpg';'*.png';'*.bmp';'*.svg';'*.*'};
[fileName,pathName] = uiputfile(filterSpec,'Save Cluster Pie Charts');
saveas(clusterPieFigureHandle,fullfile(pathName,fileName));

% --------------------------------------------------------------------
function resetPlotView_Callback(hObject, eventdata, handles)
% hObject    handle to resetPlotView (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% updateAxisPlot(projectedData,selectedMetadataColumnValues,cMap,handles.plotAxes)
if(get(handles.plot3D,'Value'))
    view(handles.plotAxes,[-37.50 30]);
else
    view(handles.plotAxes,[0 90]);
end


% --------------------------------------------------------------------
function exportClusterResults_Callback(hObject, eventdata, handles)
% hObject    handle to exportClusterResults (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
clusterResult = getappdata(handles.PhindrViewer,'clusterResult');
txtData = getappdata(handles.PhindrViewer,'txtData');
txtHeader = getappdata(handles.PhindrViewer,'txtHeader');
txtHeader = [txtHeader cellstr('Cluster Assignment')];
[fileName,pathName] = uiputfile('*.txt','Save Cluster Pie Charts');
if(isnumeric(fileName))
    return;
end
fileName = fullfile(pathName,fileName);
h = waitbar(.5,'Writing output to file..');
try
    fid = fopen(fileName,'w');
%     Write header
    
    for i = 1:numel(txtHeader)
        fprintf(fid,'%s\t',txtHeader{i});
    end
    fprintf(fid,'\n');
    for i = 1:size(txtData,1)        
        for j = 1:size(txtData,2)+1
            
            if(j <= size(txtData,2))
                fprintf(fid,'%s\t',txtData{i,j});
            else
                fprintf(fid,'%f\t',clusterResult(i,1));
            end            
        end
        fprintf(fid,'\n');
    end
    fclose(fid);
catch expc
    fclose(fid);
    rethrow(expc);
end
waitbar(1,h,'Writing output to file..');
close(h);
