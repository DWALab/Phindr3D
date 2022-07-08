function varargout = colorpicker(varargin)
% COLORPICKER MATLAB code for colorpicker.fig
%      COLORPICKER, by itself, creates a new COLORPICKER or raises the existing
%      singleton*.
%
%      H = COLORPICKER returns the handle to a new COLORPICKER or the handle to
%      the existing singleton*.
%
%      COLORPICKER('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in COLORPICKER.M with the given input arguments.
%
%      COLORPICKER('Property','Value',...) creates a new COLORPICKER or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before colorpicker_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to colorpicker_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help colorpicker

% Last Modified by GUIDE v2.5 12-Oct-2017 22:29:18

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @colorpicker_OpeningFcn, ...
                   'gui_OutputFcn',  @colorpicker_OutputFcn, ...
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


% --- Executes just before colorpicker is made visible.
function colorpicker_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to colorpicker (see VARARGIN)

% Choose default command line output for colorpicker
handles.output = hObject;
guidata(hObject, handles);
% if(isempty(varargin))
%     errordlg('Choose appropriate grouping','');
%     close(hObject);
% end
if(~isempty(varargin))
    groupNames = varargin{1};
    maps = varargin{2};
end

% Update handles structure
guidata(hObject, handles);
setappdata(hObject,'tabledata',groupNames);
setappdata(hObject,'maps',maps);
% save([pwd '\parameters.mat'],'param','-append');
data = cell(numel(groupNames),1);

for i = 1:size(data,1)
    rgb = round(maps(i,:).*255);
    hex(:,2:7) = reshape(sprintf('%02X',rgb.'),6,[]).';
    hex(:,1) = '#';
%     data(i,2:4) = num2cell([param.maps(i,:)]);    
    data(i,1) = cellstr(['<html><font color="', ...
        hex, ...
        '">', ...
        groupNames{i}, ...
        '</font></html>']);
end
set(handles.controlsTable,'Data',data);


% UIWAIT makes colorpicker wait for user response (see UIRESUME)
uiwait(handles.colorPicker);


% --- Outputs from this function are returned to the command line.
function varargout = colorpicker_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
% varargout{1} = handles.output;
varargout{1} = getappdata(handles.colorPicker,'maps');


delete(handles.colorPicker);
% varargout{2} = cellstr('PP');


% --- Executes on button press in exitColorPicker.
function exitColorPicker_Callback(hObject, eventdata, handles)
% hObject    handle to exitColorPicker (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% data = get(handles.controlsTable,'Data');
% 

% close(handles.colorPicker);

% --- Executes on button press in pushbutton2.
function pushbutton2_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% --- Executes when selected cell(s) is changed in controlsTable.
function controlsTable_CellSelectionCallback(hObject, eventdata, handles)
% hObject    handle to controlsTable (see GCBO)
% eventdata  structure with the following fields (see MATLAB.UI.CONTROL.TABLE)
%	Indices: row and column indices of the cell(s) currently selecteds
% handles    structure with handles and user data (see GUIDATA)


maps = getappdata(handles.colorPicker,'maps');
index = eventdata.Indices;
fdata = getappdata(handles.colorPicker,'tabledata');
if(~isempty(index))
    data = get(hObject,'Data');
    c = uisetcolor;  
    maps(index(1),:) = c;
    rgb = c.*255;
    hex(:,2:7) = reshape(sprintf('%02X',rgb.'),6,[]).';
    hex(:,1) = '#';
%     data(index(1),2:4) = num2cell([c]);
    
    data(index(1),1) = cellstr(['<html><font color="', ...
          hex, ...
          '">', ...
          fdata{index(1),1}, ...
          '</font></html>']);
    set(hObject,'Data',data);  
end
setappdata(handles.colorPicker,'maps',maps);


% --- Executes when user attempts to close colorPicker.
function colorPicker_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to colorPicker (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: delete(hObject) closes the figure
if(isequal(get(handles.colorPicker,'waitstatus'),'waiting'))
    uiresume(handles.colorPicker);
else
    delete(hObject);
end
% colorpicker_OutputFcn(hObject, eventdata, handles);
% close(handles.colorPicker)
