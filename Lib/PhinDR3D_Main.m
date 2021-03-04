function varargout = PhinDR3D_Main(varargin)
% PHINDR3D_MAIN MATLAB code for PhinDR3D_Main.fig
%      PHINDR3D_MAIN, by itself, creates a new PHINDR3D_MAIN or raises the existing
%      singleton*.
%
%      H = PHINDR3D_MAIN returns the handle to a new PHINDR3D_MAIN or the handle to
%      the existing singleton*.
%
%      PHINDR3D_MAIN('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in PHINDR3D_MAIN.M with the given input arguments.
%
%      PHINDR3D_MAIN('Property','Value',...) creates a new PHINDR3D_MAIN or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before PhinDR3D_Main_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to PhinDR3D_Main_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help PhinDR3D_Main

% Last Modified by GUIDE v2.5 12-Aug-2018 14:30:25

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @PhinDR3D_Main_OpeningFcn, ...
                   'gui_OutputFcn',  @PhinDR3D_Main_OutputFcn, ...
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


% --- Executes just before PhinDR3D_Main is made visible.
function PhinDR3D_Main_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to PhinDR3D_Main (see VARARGIN)

% Choose default command line output for PhinDR3D_Main
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

param = initParameters;
setappdata(hObject,'param',param);

% UIWAIT makes PhinDR3D_Main wait for user response (see UIRESUME)
% uiwait(handles.phindrMain);


% --- Outputs from this function are returned to the command line.
function varargout = PhinDR3D_Main_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in loadMetadata.
function loadMetadata_Callback(hObject, eventdata, handles)
% hObject    handle to loadMetadata (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% - Loads Metadata information and sets it to the context of main figure

% Select Input File
[filename,pth] = uigetfile('*.txt');
[ mData, imageID, metaHeader,chanInfo ] = parseMetadataFile( fullfile(pth,filename) );
if(isempty(imageID))
    errordlg('Something went wrong!!');
    return;
end

% Set application data for main figure
setappdata(handles.phindrMain,'mData',mData);
setappdata(handles.phindrMain,'imageID',imageID);
setappdata(handles.phindrMain,'metaHeader',metaHeader);
setappdata(handles.phindrMain,'chanInfo',chanInfo);
param = getappdata(handles.phindrMain,'param');


param.intensityThresholdTuningFactor = get(handles.threshSlider,'Value');
param.numChannels = numel(chanInfo.channelNames);
param.metaDataHeader = metaHeader;

selectedSlice = 1;
% setappdata(handles.phindrMain,'param',param);
% Set Display Image
uImageID = unique(imageID);
imageID2View = randperm(numel(uImageID));
imageID2View = uImageID(imageID2View(1));
setappdata(handles.phindrMain,'imageID2View',imageID2View);

[param.randFieldID, param.treatmentValues] = getTrainingFields(mData,...
                    param,imageID,[]);
param = getScalingFactorforImages( mData,imageID,param);
param = getImageThresholdValues(mData,imageID,param);
param.intensityThreshold = quantile(param.intensityThresholdValues,param.intensityThresholdTuningFactor);

image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,selectedSlice,'Slice');
                            
updateAxisImage(handles.displayAxis,image2Display,'Slice'); 
setappdata(handles.phindrMain,'currentSliceNumber',1);
setappdata(handles.phindrMain,'currentImageID',imageID2View);
set(handles.sliceSlider,'Value',1);
set(handles.threshSlider,'Value',0);
set(handles.sliceSlider,'Min',1);
set(handles.sliceSlider,'Max',sum(imageID == imageID2View));
set(handles.sliceSlider,'SliderStep',[.01 .1]);
set(handles.showSVMV,'Value',0);
setappdata(handles.phindrMain,'param',param);
msgbox('Metadata Extraction Completed','Success');

% --- Executes on button press in threshSlider.
function threshSlider_Callback(hObject, eventdata, handles)
% hObject    handle to threshSlider (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
selectedSlice = floor(get(handles.sliceSlider,'Value'));
thresholdValue = get(hObject,'Value');
param = getappdata(handles.phindrMain,'param');
metaHeader = getappdata(handles.phindrMain,'metaHeader');
chanInfo = getappdata(handles.phindrMain,'chanInfo');
mData = getappdata(handles.phindrMain,'mData');
imageID = getappdata(handles.phindrMain,'imageID');
imageID2View = getappdata(handles.phindrMain,'currentImageID');
h = waitbar(0,'Updating Image');
param.intensityThreshold = quantile(param.intensityThresholdValues,thresholdValue);
setappdata(handles.phindrMain,'param',param);
waitbar(.5,h);
image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,selectedSlice,'Slice');                            
updateAxisImage(handles.displayAxis,image2Display,'Slice');
waitbar(1,h);
showSVMV_Callback(handles.showSVMV,eventdata,handles);
close(h);


% --- Executes on button press in setVoxelParam.
function setVoxelParam_Callback(hObject, eventdata, handles)
% hObject    handle to setVoxelParam (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('Metadata not found!!');
    return;
end

% Get stored data from figure
param = getappdata(handles.phindrMain,'param');
metaHeader = getappdata(handles.phindrMain,'metaHeader');
chanInfo = getappdata(handles.phindrMain,'chanInfo');
mData = getappdata(handles.phindrMain,'mData');
imageID = getappdata(handles.phindrMain,'imageID');
imageID2View = getappdata(handles.phindrMain,'currentImageID');

selectedSlice = floor(get(handles.sliceSlider,'Value'));
m = true(1,numel(metaHeader));
m(1,chanInfo.channelColNumber)= false;

[~, param] = setParameters(param,metaHeader(1,m));
if(param.intensityNormPerTreatment)
    param.treatmentColNameForNormalization = strcmpi(metaHeader,...
        param.treatmentColNameForNormalization);
    param.grpIndicesForIntensityNormalization = getGroupIndices(mData(:,...
        param.treatmentColNameForNormalization),unique(mData(:,...
        param.treatmentColNameForNormalization)));
end
[param.randFieldID, param.treatmentValues] = getTrainingFields(mData,...
                    param,imageID,param.trainingColforImageCategories);
param = getScalingFactorforImages( mData,imageID,param);
param = getImageThresholdValues(mData,imageID,param);
param.superVoxelPerField = floor(param.randTrainingSuperVoxel./param.randTrainingFields);
param.intensityThreshold = quantile(param.intensityThresholdValues,param.intensityThresholdTuningFactor);

image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,selectedSlice,'Slice');
                            
updateAxisImage(handles.displayAxis,image2Display,'Slice'); 
% Rescale Intensity --- 

% Apply lower threshold --- 
set(handles.threshSlider,'Enable','On');
setappdata(handles.phindrMain,'param',param);

% --- Executes on button press in extractFeatures.
function extractFeatures_Callback(hObject, eventdata, handles)
% hObject    handle to extractFeatures (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('Metadata not found!!');
    return;
end
[outputFileName,outputDir] = uiputfile('*.txt','Select Output File');

param = getappdata(handles.phindrMain,'param');
metaHeader = getappdata(handles.phindrMain,'metaHeader');
% chanInfo = getappdata(handles.phindrMain,'chanInfo');
mData = getappdata(handles.phindrMain,'mData');
allImageId = getappdata(handles.phindrMain,'imageID');

% Perform Training
param = getPixelBinCenters(mData, allImageId, param);
param = getSuperVoxelBinCenters(mData,allImageId,param);
param = getMegaVoxelBinCenters(mData,allImageId,param);
param.metaDataHeader = metaHeader;

% Extract Features & write Files
extractImageLevelTextureFeatures(mData,allImageId,param,outputFileName,outputDir);
uiwait(msgbox('Operation Completed','Success','modal'));



% --- Executes during object creation, after setting all properties.
function text1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to text1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


% --------------------------------------------------------------------
function m1_Callback(hObject, eventdata, handles)
% hObject    handle to m1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function ch1_Callback(hObject, eventdata, handles)
% hObject    handle to ch1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function setChanColor_Callback(hObject, eventdata, handles)
% hObject    handle to setChannelColors (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function createMetadata_Callback(hObject, eventdata, handles)
% hObject    handle to createMetadata (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
metadataExtractor

% --------------------------------------------------------------------
function p1_Callback(hObject, eventdata, handles)
% hObject    handle to p1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function minScale_Callback(hObject, eventdata, handles)
% hObject    handle to minScale (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
param = getappdata(handles.phindrMain,'param');
prompt = {'Min Adjustment Value','Min Adjustment Value'};
title = 'Set Min/Max Scaling Adjustment';
def = cellstr(num2str([param.minScaleQuantile;param.maxScaleQuantile]));
answer = inputdlg(prompt,title,1,def);
answer = str2num(char(answer));
ii = answer<.01;
answer(ii) = .05;
ii = answer>.99;
answer(ii) = .99;
param.minScaleQuantile = answer(1);
param.maxScaleQuantile = answer(2);
setappdata(handles.phindrMain,'param',param);



% --------------------------------------------------------------------
function voxelParam_Callback(hObject, eventdata, handles)
% hObject    handle to voxelParam (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function otherParam_Callback(hObject, eventdata, handles)
% hObject    handle to otherParam (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function disGamma_Callback(hObject, eventdata, handles)
% hObject    handle to disGamma (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function im2View_Callback(hObject, eventdata, handles)
% hObject    handle to nextImage (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
mData = setappdata(handles.viewData,'mData');
param = setappdata(handles.viewData,'param');
setappdata(handles.viewData,'metaHeader',metaHeader);
setappdata(handles.viewData,'chanInfo',chanInfo);
[sel, ok] = listdlg('ListString')
param.trainingColforImageCategories
channels = chanInfo.channelColNumber;

stackCol = strcmpi(metaHeader,'Stack') | strcmpi(metaHeader,'Stacks');
stck = cell2mat(mData(:,stackCol));
ii = stck == min(unique(stck));
uImageID = imageID(ii,1);
numNonChannel = true(1,size(mData,2));
numNonChannel(1,chanInfo.channelColNumber) = false;
mData = mData(ii,numNonChannel);


% --------------------------------------------------------------------
function Untitled_3_Callback(hObject, eventdata, handles)
% hObject    handle to nextImage (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function Untitled_4_Callback(hObject, eventdata, handles)
% hObject    handle to setChannelColors (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function loadPreviousParameters_Callback(hObject, eventdata, handles)
% hObject    handle to loadPreviousParameters (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function C_Callback(hObject, eventdata, handles)
% hObject    handle to C (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in setChannelColors.
function setChannelColors_Callback(hObject, eventdata, handles)
% hObject    handle to setChannelColors (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('Metadata not found!!');
    return;
end
selectedSlice = floor(get(handles.sliceSlider,'Value'));
chanInfo = getappdata(handles.phindrMain,'chanInfo');
[chanInfo.channelColors] = colorpicker(chanInfo.channelNames',chanInfo.channelColors);
setappdata(handles.phindrMain,'chanInfo',chanInfo);  

param = getappdata(handles.phindrMain,'param');
mData = getappdata(handles.phindrMain,'mData');
imageID = getappdata(handles.phindrMain,'imageID');
chanInfo = getappdata(handles.phindrMain,'chanInfo');    
imageID2View = getappdata(handles.phindrMain,'currentImageID');
metaHeader = getappdata(handles.phindrMain,'metaHeader');
image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,selectedSlice,'Slice');
                            
updateAxisImage(handles.displayAxis,image2Display,'Slice');   


% --- Executes on button press in pushbutton9.
function pushbutton9_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton9 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in showSVMV.
function showSVMV_Callback(hObject, eventdata, handles)
% hObject    handle to showSVMV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of showSVMV
tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('Metadata not found!!');
    return;
end
valueOfCheckBox = get(hObject,'Value');
param = getappdata(handles.phindrMain,'param');
if(valueOfCheckBox)
    image2Display = getimage(handles.displayAxis);
    
    image2Display = getImageWithSVMVOverlay(image2Display,param,'SV');
    h = imshow(image2Display,[],'Parent',handles.displayAxis); 
    set(h,'hittest','off');
    set(handles.displayAxis,'Visible','on');
    set(handles.displayAxis,'XTick',[]);
    set(handles.displayAxis,'YTick',[]);
else
    selectedSlice = floor(get(handles.sliceSlider,'Value'));
    mData = getappdata(handles.phindrMain,'mData');
    imageID = getappdata(handles.phindrMain,'imageID');
    chanInfo = getappdata(handles.phindrMain,'chanInfo');    
    imageID2View = getappdata(handles.phindrMain,'currentImageID');
    metaHeader = getappdata(handles.phindrMain,'metaHeader');
    image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,selectedSlice,'Slice');                            
    updateAxisImage(handles.displayAxis,image2Display,'Slice'); 
    
end


% --- Executes on button press in nextImage.
function nextImage_Callback(hObject, eventdata, handles)
% hObject    handle to nextImage (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
selectedSlice=1;
tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('Metadata not found!!');
    return;
end
% v = set(handles.threshSlider,'Value',0);
param = getappdata(handles.phindrMain,'param');
mData = getappdata(handles.phindrMain,'mData');
imageID = getappdata(handles.phindrMain,'imageID');
chanInfo = getappdata(handles.phindrMain,'chanInfo');
currImageID2View = getappdata(handles.phindrMain,'currentImageID'); 

% Set Display Image
uImageID = unique(imageID);
k = randperm(numel(uImageID));
imageID2View = uImageID(k(1));
if(imageID2View == currImageID2View)
    imageID2View = uImageID(k(2));
end
metaHeader = getappdata(handles.phindrMain,'metaHeader');
image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,selectedSlice,'Slice');                            
    updateAxisImage(handles.displayAxis,image2Display,'Slice'); 
setappdata(handles.phindrMain,'currentImageID',imageID2View);
set(handles.sliceSlider,'Value',1);

showSVMV_Callback(handles.showSVMV,eventdata,handles);

% --- Executes on slider movement.
function sliceSlider_Callback(hObject, eventdata, handles)
% hObject    handle to sliceSlider (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('Metadata not found!!');
    return;
end
selectedSlice = floor(get(hObject,'Value'));
param = getappdata(handles.phindrMain,'param');
mData = getappdata(handles.phindrMain,'mData');
imageID = getappdata(handles.phindrMain,'imageID');
chanInfo = getappdata(handles.phindrMain,'chanInfo');    
imageID2View = getappdata(handles.phindrMain,'currentImageID');
metaHeader = getappdata(handles.phindrMain,'metaHeader');
image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,selectedSlice,'Slice');                            
updateAxisImage(handles.displayAxis,image2Display,'Slice');  
if(get(handles.showSVMV,'Value'))
showSVMV_Callback(handles.showSVMV,eventdata,handles);
end
if(get(handles.showMV,'Value'))
showMV_Callback(handles.showMV,eventdata,handles);
end


% --- Executes during object creation, after setting all properties.
function sliceSlider_CreateFcn(hObject, eventdata, handles)
% hObject    handle to sliceSlider (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --------------------------------------------------------------------
function exportAxis_Callback(hObject, eventdata, handles)
% hObject    handle to exportAxis (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
h = figure;
h1 = copyobj(handles.displayAxis, h);
set(h1, 'Units', 'normalized', 'Position', [.1 .1 .8 .8]);
filterSpec = {'*.fig';'*.jpg';'*.png';'*.bmp';'*.svg';'*.*'};
[fileName,pathName] = uiputfile(filterSpec);

saveas(h1,fullfile(pathName,fileName));
% close(h1);
% --------------------------------------------------------------------
function FileMenu_Callback(hObject, eventdata, handles)
% hObject    handle to FileMenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function Untitled_2_Callback(hObject, eventdata, handles)
% hObject    handle to Untitled_2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function Untitled_5_Callback(hObject, eventdata, handles)
% hObject    handle to Untitled_5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function importParameters_Callback(hObject, eventdata, handles)
% hObject    handle to importParameters (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
[filename,inputDir] = uigetfile('*.mat');
s = load(fullfile(inputDir,filename));
setappdata(handles.phindrMain,'param',s.param);
% --------------------------------------------------------------------
function exportParameters_Callback(hObject, eventdata, handles)
% hObject    handle to exportParameters (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('No parameters to export!!');
    return;
end
[filename,inputDir] = uiputfile('*.mat');
filename = fullfile(inputDir,filename);
param = getappdata(handles.phindrMain,'param');
save(filename,'param'); 

% --------------------------------------------------------------------
function importSession_Callback(hObject, eventdata, handles)
% hObject    handle to importSession (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
[filename,inputDir] = uigetfile('*.mat');
s = load(fullfile(inputDir,filename));
setappdata(handles.phindrMain,'mData',s.mData);
setappdata(handles.phindrMain,'imageID',s.imageID);
setappdata(handles.phindrMain,'metaHeader',s.metaHeader);
setappdata(handles.phindrMain,'chanInfo',s.chanInfo);
setappdata(handles.phindrMain,'param',s.param);


% --------------------------------------------------------------------
function exportSession_Callback(hObject, eventdata, handles)
% hObject    handle to importParameters (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('No variables to export!!');
    return;
end
[filename,inputDir] = uiputfile('*.mat');
filename = fullfile(inputDir,filename);

mData = getappdata(handles.phindrMain,'mData');
imageID = getappdata(handles.phindrMain,'imageID');
metaHeader = getappdata(handles.phindrMain,'metaHeader');
chanInfo = getappdata(handles.phindrMain,'chanInfo');
param = getappdata(handles.phindrMain,'param');
save(filename,'mData','imageID','metaHeader','chanInfo','param'); 


% --------------------------------------------------------------------
function viewResults_Callback(hObject, eventdata, handles)
% hObject    handle to viewResults (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
PhindrViewer;


% --------------------------------------------------------------------
function aboutPhindr_Callback(hObject, eventdata, handles)
% hObject    handle to aboutPhindr (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
message = sprintf('    Phindr3D Version 1.0\n');
message = [message sprintf('    David Andrews Lab\n    University Of Toronto')];
msgbox(message,'About');



function displayeFilename_Callback(hObject, eventdata, handles)
% hObject    handle to displayeFilename (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of displayeFilename as text
%        str2double(get(hObject,'String')) returns contents of displayeFilename as a double


% --- Executes during object creation, after setting all properties.
function displayeFilename_CreateFcn(hObject, eventdata, handles)
% hObject    handle to displayeFilename (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in showMV.
function showMV_Callback(hObject, eventdata, handles)
% hObject    handle to showMV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of showMV
tf = isappdata(handles.phindrMain,'imageID');
if(~tf)
    errordlg('Metadata not found!!');
    return;
end
valueOfCheckBox = get(hObject,'Value');
param = getappdata(handles.phindrMain,'param');
if(valueOfCheckBox)
    image2Display = getimage(handles.displayAxis);
    
    image2Display = getImageWithSVMVOverlay(image2Display,param,'MV');
    h = imshow(image2Display,[],'Parent',handles.displayAxis); 
    set(h,'hittest','off');
    set(handles.displayAxis,'Visible','on');
    set(handles.displayAxis,'XTick',[]);
    set(handles.displayAxis,'YTick',[]);
else
    selectedSlice = floor(get(handles.sliceSlider,'Value'));
    mData = getappdata(handles.phindrMain,'mData');
    imageID = getappdata(handles.phindrMain,'imageID');
    chanInfo = getappdata(handles.phindrMain,'chanInfo');    
    imageID2View = getappdata(handles.phindrMain,'currentImageID');
    metaHeader = getappdata(handles.phindrMain,'metaHeader');
    image2Display = getImage2Display(mData,metaHeader,param,imageID2View,imageID,...
                                chanInfo,selectedSlice,'Slice');                            
    updateAxisImage(handles.displayAxis,image2Display,'Slice'); 
    
end
