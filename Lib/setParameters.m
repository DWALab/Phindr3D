function varargout = setParameters(varargin)
% SETPARAMETERS MATLAB code for setParameters.fig
%      SETPARAMETERS, by itself, creates a new SETPARAMETERS or raises the existing
%      singleton*.
%
%      H = SETPARAMETERS returns the handle to a new SETPARAMETERS or the handle to
%      the existing singleton*.
%
%      SETPARAMETERS('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in SETPARAMETERS.M with the given input arguments.
%
%      SETPARAMETERS('Property','Value',...) creates a new SETPARAMETERS or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before setParameters_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to setParameters_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help setParameters

% Last Modified by GUIDE v2.5 06-Jun-2018 11:23:55

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @setParameters_OpeningFcn, ...
                   'gui_OutputFcn',  @setParameters_OutputFcn, ...
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


% --- Executes just before setParameters is made visible.
function setParameters_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to setParameters (see VARARGIN)

% Choose default command line output for setParameters
handles.output = hObject;
% Update handles structure
guidata(hObject, handles);
m = size(varargin);
if(sum(m)==0)
    
end
param = varargin{1};
param.header = varargin{2};
setappdata(handles.setParam,'param',param);
set(handles.intensityCol,'String',varargin{2});
set(handles.trainingCol,'String',varargin{2});

% Set Values from Parameter file
param = getappdata(handles.setParam,'param');

setParameterValues(handles,param);

% setappdata(handles.setParam,'header',varargin{2});
% UIWAIT makes setParameters wait for user response (see UIRESUME)
uiwait(handles.setParam);


% --- Outputs from this function are returned to the command line.
function varargout = setParameters_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;
varargout{2} = getappdata(handles.setParam,'param');
delete(hObject)

function mvCat_Callback(hObject, eventdata, handles)
% hObject    handle to mvCat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of mvCat as text
%        str2double(get(hObject,'String')) returns contents of mvCat as a double


% --- Executes during object creation, after setting all properties.
function mvCat_CreateFcn(hObject, eventdata, handles)
% hObject    handle to mvCat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function svCat_Callback(hObject, eventdata, handles)
% hObject    handle to svCat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of svCat as text
%        str2double(get(hObject,'String')) returns contents of svCat as a double


% --- Executes during object creation, after setting all properties.
function svCat_CreateFcn(hObject, eventdata, handles)
% hObject    handle to svCat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function svX_Callback(hObject, eventdata, handles)
% hObject    handle to svX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of svX as text
%        str2double(get(hObject,'String')) returns contents of svX as a double


% --- Executes during object creation, after setting all properties.
function svX_CreateFcn(hObject, eventdata, handles)
% hObject    handle to svX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function svY_Callback(hObject, eventdata, handles)
% hObject    handle to svY (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of svY as text
%        str2double(get(hObject,'String')) returns contents of svY as a double


% --- Executes during object creation, after setting all properties.
function svY_CreateFcn(hObject, eventdata, handles)
% hObject    handle to svY (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function svZ_Callback(hObject, eventdata, handles)
% hObject    handle to svZ (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of svZ as text
%        str2double(get(hObject,'String')) returns contents of svZ as a double


% --- Executes during object creation, after setting all properties.
function svZ_CreateFcn(hObject, eventdata, handles)
% hObject    handle to svZ (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function mvX_Callback(hObject, eventdata, handles)
% hObject    handle to mvX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of mvX as text
%        str2double(get(hObject,'String')) returns contents of mvX as a double


% --- Executes during object creation, after setting all properties.
function mvX_CreateFcn(hObject, eventdata, handles)
% hObject    handle to mvX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function mvY_Callback(hObject, eventdata, handles)
% hObject    handle to mvY (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of mvY as text
%        str2double(get(hObject,'String')) returns contents of mvY as a double


% --- Executes during object creation, after setting all properties.
function mvY_CreateFcn(hObject, eventdata, handles)
% hObject    handle to mvY (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function mvZ_Callback(hObject, eventdata, handles)
% hObject    handle to mvZ (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of mvZ as text
%        str2double(get(hObject,'String')) returns contents of mvZ as a double


% --- Executes during object creation, after setting all properties.
function mvZ_CreateFcn(hObject, eventdata, handles)
% hObject    handle to mvZ (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function voxCat_Callback(hObject, eventdata, handles)
% hObject    handle to voxCat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of voxCat as text
%        str2double(get(hObject,'String')) returns contents of voxCat as a double


% --- Executes during object creation, after setting all properties.
function voxCat_CreateFcn(hObject, eventdata, handles)
% hObject    handle to voxCat (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function trainImages_Callback(hObject, eventdata, handles)
% hObject    handle to trainImages (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of trainImages as text
%        str2double(get(hObject,'String')) returns contents of trainImages as a double


% --- Executes during object creation, after setting all properties.
function trainImages_CreateFcn(hObject, eventdata, handles)
% hObject    handle to trainImages (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in intensityNormPerTreatment.
function intensityNormPerTreatment_Callback(hObject, eventdata, handles)
% hObject    handle to intensityNormPerTreatment (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of intensityNormPerTreatment
if(get(hObject,'Value'))
    set(handles.intensityCol,'Enable','On');
else
    set(handles.intensityCol,'Enable','Off');
end



% --- Executes on button press in trainPerCondition.
function trainPerCondition_Callback(hObject, eventdata, handles)
% hObject    handle to trainPerCondition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of trainPerCondition
if(get(hObject,'Value'))
    set(handles.trainingCol,'Enable','On');
else
    set(handles.trainingCol,'Enable','Off');
end


% --- Executes on selection change in intensityCol.
function intensityCol_Callback(hObject, eventdata, handles)
% hObject    handle to intensityCol (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns intensityCol contents as cell array
%        contents{get(hObject,'Value')} returns selected item from intensityCol


% --- Executes during object creation, after setting all properties.
function intensityCol_CreateFcn(hObject, eventdata, handles)
% hObject    handle to intensityCol (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in trainingCol.
function trainingCol_Callback(hObject, eventdata, handles)
% hObject    handle to trainingCol (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns trainingCol contents as cell array
%        contents{get(hObject,'Value')} returns selected item from trainingCol


% --- Executes during object creation, after setting all properties.
function trainingCol_CreateFcn(hObject, eventdata, handles)
% hObject    handle to trainingCol (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in resetParam.
function resetParam_Callback(hObject, eventdata, handles)
% hObject    handle to resetParam (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
param = getappdata(handles.setParam,'param');
setappdata(handles.setParam,'param',param);
setParameterValues(handles,param);

% --- Executes on button press in closeFig.
function closeFig_Callback(~, ~, handles)
% hObject    handle to closeFig (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Set Parameters
param = getappdata(handles.setParam,'param');

param.tileX = str2num(get(handles.svX,'String'));
param.tileY = str2num(get(handles.svY,'String'));
param.tileZ = str2num(get(handles.svZ,'String'));

param.numVoxelBins = str2num(get(handles.voxCat,'String'));
param.numSuperVoxelBins = str2num(get(handles.svCat,'String'));
param.numMegaVoxelBins = str2num(get(handles.mvCat,'String'));


param.megaVoxelTileX = str2num(get(handles.mvX,'String'));
param.megaVoxelTileY = str2num(get(handles.mvY,'String'));
param.megaVoxelTileZ = str2num(get(handles.mvZ,'String'));

param.countBackground = get(handles.countBkg,'Value');
param.intensityNormPerTreatment = get(handles.intensityNormPerTreatment,'Value');
param.trainingPerColumn = get(handles.trainPerCondition,'Value');

param.randTrainingFields = str2num(get(handles.trainImages,'String'));

v = get(handles.intensityCol,'String');
param.treatmentColNameForNormalization = v(get(handles.intensityCol,'value')); 
v = get(handles.trainingCol,'String');
param.trainingColforImageCategories = v(get(handles.trainingCol,'value'));

if(~param.intensityNormPerTreatment)
    param.treatmentColNameForNormalization = '';
end

if(~param.trainingPerColumn)
    param.trainingColforImageCategories = '';
end

setappdata(handles.setParam,'param',param);


% setappdata(handles.setParam,'aa',1);
uiresume(handles.setParam);


% --- Executes on button press in countBkg.
function countBkg_Callback(hObject, eventdata, handles)
% hObject    handle to countBkg (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of countBkg
