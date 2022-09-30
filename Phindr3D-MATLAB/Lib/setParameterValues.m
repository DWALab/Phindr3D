function setParameterValues(handles,param)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
set(handles.svX,'String',param.tileX);
set(handles.svY,'String',param.tileY);
set(handles.svZ,'String',param.tileZ);

set(handles.voxCat,'String',param.numVoxelBins);
set(handles.svCat,'String',param.numSuperVoxelBins);
set(handles.mvCat,'String',param.numMegaVoxelBins);

set(handles.mvX,'String',param.megaVoxelTileX);
set(handles.mvY,'String',param.megaVoxelTileY);
set(handles.mvZ,'String',param.megaVoxelTileZ);

set(handles.countBkg,'Value',param.countBackground)
set(handles.intensityNormPerTreatment,'Value',param.intensityNormPerTreatment)
set(handles.trainPerCondition,'Value',param.trainingPerColumn)

set(handles.trainImages,'String',param.randTrainingFields);

ii = find(strcmpi(param.header,param.treatmentColNameForNormalization));
if(~isempty(ii))
    set(handles.intensityCol,'Value',ii);
    set(handles.intensityCol,'Enable','On');
    set(handles.intensityNormPerTreatment,'Value',1);
else
    set(handles.intensityCol,'Value',1);
    set(handles.intensityCol,'Enable','Off');
    set(handles.intensityNormPerTreatment,'Value',0);
end

ii = find(strcmpi(param.header,param.trainingColforImageCategories));
if(~isempty(ii))
    set(handles.trainingCol,'Value',ii);
    set(handles.trainingCol,'Enable','On');
    set(handles.trainPerCondition,'Value',1);
else
    set(handles.trainingCol,'Value',1);
    set(handles.trainingCol,'Enable','Off');
    set(handles.trainPerCondition,'Value',0);
end
end

