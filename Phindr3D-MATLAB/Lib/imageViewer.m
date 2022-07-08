function varargout = imageViewer(varargin)
% IMAGEVIEWER MATLAB code for imageViewer.fig
%      IMAGEVIEWER, by itself, creates a new IMAGEVIEWER or raises the existing
%      singleton*.
%
%      H = IMAGEVIEWER returns the handle to a new IMAGEVIEWER or the handle to
%      the existing singleton*.
%
%      IMAGEVIEWER('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in IMAGEVIEWER.M with the given input arguments.
%
%      IMAGEVIEWER('Property','Value',...) creates a new IMAGEVIEWER or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before imageViewer_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to imageViewer_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help imageViewer

% Last Modified by GUIDE v2.5 22-Jul-2018 21:33:10

% Begin initialization code - DO NOT EDIT
gui_Singleton = 0;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @imageViewer_OpeningFcn, ...
                   'gui_OutputFcn',  @imageViewer_OutputFcn, ...
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


% --- Executes just before imageViewer is made visible.
function imageViewer_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to imageViewer (see VARARGIN)

% Choose default command line output for imageViewer
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);
if(~isempty(varargin))
    channelNames = varargin{2}';
    imageFileNames = varargin{1};   
    
else
    errordlg('No Image Selected','');
    return;
end
selectedChannels = true(1,numel(channelNames));
if(isappdata(0,'channelColorValue'))
    channelColorValue = getappdata(0,'channelColorValue');
else
    channelColorValue = lines(numel(channelNames));
end
% setappdata(handles.imageViewer,'channelColorValue',channelColorValue);
setappdata(handles.imageViewer,'imageFileNames',imageFileNames);
setappdata(handles.imageViewer,'channelNames',channelNames);
setappdata(handles.imageViewer,'selectedChannels',selectedChannels);
set(handles.sliceSlider,'min',1);
set(handles.sliceSlider,'max',size(imageFileNames,1));
stepSize = (size(imageFileNames,1)-1)/2;
set(handles.sliceSlider,'SliderStep',[.01 .1]);
set(handles.sliceSlider,'Value',1);
set(handles.imageAxes,'XTickLabel',[]);
set(handles.imageAxes,'YTickLabel',[]);



setTextInformation(handles.infotext,imageFileNames,channelNames,channelColorValue,...
                                    selectedChannels,'Slice');
setChannelInformation(handles.channelNameDisplay,channelNames,channelColorValue,...
                                    selectedChannels);
setImageView(imageFileNames(1,:),channelColorValue,'Slice',selectedChannels,handles.imageAxes); 
% UIWAIT makes imageViewer wait for user response (see UIRESUME)
% uiwait(handles.imageViewer);


% --- Outputs from this function are returned to the command line.
function varargout = imageViewer_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on slider movement.
function sliceSlider_Callback(hObject, eventdata, handles)
% hObject    handle to sliceSlider (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
sliceNumber = floor(get(hObject,'Value'));
selectedChannels = getappdata(handles.imageViewer,'selectedChannels');
imageFileNames = getappdata(handles.imageViewer,'imageFileNames');
imageFileNames = imageFileNames(sliceNumber,:);
channelColorValue = getappdata(0,'channelColorValue');
setImageView(imageFileNames,channelColorValue,'Slice',selectedChannels,handles.imageAxes);

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
function channelColors_Callback(~, ~, handles)
% hObject    handle to channelColors (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
channelNames = getappdata(handles.imageViewer,'channelNames');
channelColorValue = getappdata(0,'channelColorValue');
[channelColorValue] = colorpicker(unique(channelNames),channelColorValue);
setappdata(0,'channelColorValue',channelColorValue);
viewType_SelectionChangedFcn([], [], handles);

% --------------------------------------------------------------------
function channelColor_Callback(hObject, eventdata, handles)
% hObject    handle to channelColor (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --------------------------------------------------------------------
function colorContextMenu_Callback(hObject, eventdata, handles)
% hObject    handle to colorContextMenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes when selected object is changed in viewType.
function viewType_SelectionChangedFcn(~, ~, handles)
% hObject    handle to the selected object in viewType 
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
selectedViewType = get(get(handles.viewType,'SelectedObject'),'String');
if(strcmpi(selectedViewType,'Slice'))
    set(handles.sliceSlider,'Enable','On');
else
    set(handles.sliceSlider,'Enable','Off');
end
channelNames = getappdata(handles.imageViewer,'channelNames');
selectedChannels = getappdata(handles.imageViewer,'selectedChannels');
imageFileNames = getappdata(handles.imageViewer,'imageFileNames');
channelColorValue = getappdata(0,'channelColorValue');
setImageView(imageFileNames,channelColorValue,selectedViewType,selectedChannels,handles.imageAxes);
setTextInformation(handles.infotext,imageFileNames,channelNames,channelColorValue,...
                                    selectedChannels,selectedViewType);
setChannelInformation(handles.channelNameDisplay,channelNames,channelColorValue,...
                                    selectedChannels);                                

% --------------------------------------------------------------------
function selectChannels_Callback(~, ~, handles)
% hObject    handle to selectChannels (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
selectedViewType = get(get(handles.viewType,'SelectedObject'),'String');
channelNames = getappdata(handles.imageViewer,'channelNames');
selectedChannels = true(1,numel(channelNames));
imageFileNames = getappdata(handles.imageViewer,'imageFileNames');
channelColorValue = getappdata(0,'channelColorValue');
[selection,~] = listdlg('ListString',channelNames,'SelectionMode','Multiple',...
                        'Name','Select Channels To Remove','ListSize',[300 300]);
if(numel(selection) == numel(channelNames))  
    errordlg('No Channel to display !!','','modal');
    return;
end
selectedChannels(1,selection) = false;
setImageView(imageFileNames,channelColorValue,selectedViewType,selectedChannels,handles.imageAxes);
% Update Editable Text

% --------------------------------------------------------------------
function exportImage_Callback(~, ~, handles)
% hObject    handle to exportImage (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
h = figure;
h1 = copyobj(handles.imageAxes, h);
axis off;
set(h1, 'Units', 'normalized', 'Position', [.1 .1 .8 .8]);
filterSpec = {'*.fig';'*.jpg';'*.png';'*.bmp';'*.svg';'*.*'};
[fileName,pathName] = uiputfile(filterSpec);
saveas(h1,fullfile(pathName,fileName));


% --- Executes on selection change in channelNameDisplay.
function channelNameDisplay_Callback(hObject, eventdata, handles)
% hObject    handle to channelNameDisplay (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns channelNameDisplay contents as cell array
%        contents{get(hObject,'Value')} returns selected item from channelNameDisplay


% --- Executes during object creation, after setting all properties.
function channelNameDisplay_CreateFcn(hObject, eventdata, handles)
% hObject    handle to channelNameDisplay (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
