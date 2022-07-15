# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of src <https://github.com/DWALab/Phindr3D>.
#
# src is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# src is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with src.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import numpy as np
import tifffile as tf
from scipy import ndimage
from .SegmentationFunctions import *

class Segmentation:
    """This class ...
       Static methods that draw closely from transliterations of the MATLAB functions
       can be found in the SegmentationFunctions class."""

    def __init__(self):
        """Segmentation class constructor"""
        self.defaultSettings = {
            'min_area_spheroid':200.0,
            'intensity_threshold':1000.0,
            'radius_spheroid':75.0,
            'smoothin_param':0.01,
            'scale_spheroid':1.0,
            'entropy_threshold':1.0,
            'max_img_fraction':0.25,
            'seg_Channel':'allChannels'
            }
        self.settings = self.defaultSettings
        self.metadata = None
        self.outputDir = None
        self.labDir = None
        self.segDir = None
        self.segmentationSuccess = False
        self.focusIms = {} #key = image ID, val = imagepath
        self.labelIms = {} #same same.
        self.allIDs = [] 
        self.IDidx = None
        # end constructor
    
    def saveSettings(self, outputpath):
        with open(outputpath, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def loadSettings(self, settingJsonPath):
        with open(settingJsonPath, 'r') as f:
            newsettings = json.load(f)
        self.settings = newsettings
    
    def createSubfolders(self):
        self.labDir = os.path.join(self.outputDir, 'LabelledImages')
        self.segDir = os.path.join(self.outputDir, 'SegmentedImages')
        os.makedirs(self.labDir, exist_ok=True)
        os.makedirs(self.segDir, exist_ok=True)
    
    def getCurrentIMs(self):
        if self.allIDs == []:
            return None, None
        else:
            return tf.imread(self.focusIms[self.allIDs[self.IDidx]]), tf.imread(self.labelIms[self.allIDs[self.IDidx]])
    
    def getNextIMs(self):
        if self.allIDs == []:
            return None, None
        else:
            if self.IDidx == len(self.allIDs)-1:
                self.IDidx = 0
            else:
                self.IDidx += 1
            return tf.imread(self.focusIms[self.allIDs[self.IDidx]]), tf.imread(self.labelIms[self.allIDs[self.IDidx]])

    def getPrevIMs(self):
        if self.allIDs == []:
            return None, None
        else:
            if self.IDidx == 0:
                self.IDidx = len(self.allIDs)-1
            else:
                self.IDidx -= 1
            return tf.imread(self.focusIms[self.allIDs[self.IDidx]]), tf.imread(self.labelIms[self.allIDs[self.IDidx]])

    def RunSegmentation(self, mdata):
        try: 
            for id in mdata.images:
                imstack = mdata.images[id]
                if self.settings['seg_Channel'] == 'allChannels':
                    IM, focusIndex = getfsimage_multichannel(imstack)
                else:
                    IM, focusIndex = getfsimage(imstack, self.settings['seg_channel'])
                L = getSegmentedOverlayImage(IM, self.settings)
                uLabels = np.unique(L)
                uLabels = uLabels[uLabels != 0]
                numObjects = len(uLabels)
                ll = []
                for iObjects in range(numObjects):
                    nL = (L == uLabels[iObjects]) #nL is a binary map
                    if np.sum(nL) > (L.size * self.settings['max_img_fraction']):
                        L[L == uLabels[iObjects]] = 0
                    else:
                        ll.append( getFocusplanesPerObjectMod(nL, focusIndex) )
                ll = np.array(ll)
                numObjects = len(ll)

                zVals = list(imstack.stackLayers.keys())
                channels = list(imstack.stackLayers[zVals[0]].channels.keys())
                otherparams = imstack.stackLayers[zVals[0]].otherparams
                filenameParts = []
                for param in otherparams:
                    part = f'{param[0]}{otherparams[param]}'
                    filenameParts.append(part)
                if numObjects > 0:
                    SEdil = morph.disk(25) # this structuring element can be made larger if needed.
                    L = cv.dilate(L, SEdil)
                    fstruct = ndimage.find_objects(L.astype(int))
                    for iObjects in range(numObjects):
                        for iPlanes in range(int(ll[iObjects, 0]), int(ll[iObjects, 1]+1)):
                            for chan in channels:
                                IM1 = io.imread( imstack.stackLayers[iPlanes].channels[chan].channelpath )
                                IM2 = IM1[fstruct[iObjects]]
                                tmpparts = filenameParts.copy()
                                tmpparts.append(f'Z{iPlanes}')
                                tmpparts.append(f'CH{chan}')
                                tmpparts.append(f'ID{id}')
                                tmpparts.append(f'OB{iObjects+1}')
                                obFileName = '__'.join(tmpparts)
                                obFileName = obFileName + '.tiff'
                                tf.imwrite(os.path.join(self.segDir, obFileName), IM2)
                        tmpparts = filenameParts.copy()
                        tmpparts.append(f'ID{id}')
                        tmpparts.append(f'OB{iObjects+1}')
                        obFileName = '__'.join(tmpparts)
                        obFileName = obFileName + '.tiff'
                        IML = L[fstruct[iObjects]]
                        tf.imwrite(os.path.join(self.labDir, obFileName), IML)
                allobsname = filenameParts.copy()
                focusname = filenameParts.copy()
                allobsname.append(f'ID{id}')
                focusname.append(f'ID{id}')
                allobsname.append(f'All_{numObjects}_Objects')
                focusname.append('FocusIM')
                IML = L
                objFileName = os.path.join(self.labDir, ('__'.join(allobsname) + '.tiff'))
                focFileName = os.path.join(self.labDir, ('__'.join(focusname) + '.tiff'))
                tf.imwrite(objFileName, IML)
                tf.imwrite(focFileName, IM)
                self.focusIms[id] = focFileName
                self.labelIms[id] = objFileName
            self.allIDs = list(self.focusIms.keys())
            self.IDidx = 0
            self.segmentationSuccess = True
        except:
            self.allIDs = []
            self.IDidx = None
            self.segmentationSuccess = False

    # End RunSegmentation




# end class Segmentation

if __name__ == '__main__':
    """Tests of the Segmentation class that can be run directly."""
    from Data import Metadata
    
    mdata = Metadata()
    segtest = Segmentation()

    segtest.outputDir = 'testdata\\segmentation_tests\\check_results'
    mdatafile = 'testdata\\segmentation_tests\\segtestmdata.txt'

    mdata.loadMetadataFile(mdatafile)
    print(f'Loading segmentation test images metadata success? ... {mdata.metadataLoadSuccess}')

    segtest.createSubfolders()
    segtest.RunSegmentation(mdata)
    print(f'Segmentation success? ... {segtest.segmentationSuccess}')
    for c, e in zip(os.listdir(segtest.labDir), os.listdir('testdata\\segmentation_tests\\expect_results\\LabelledImages')):
        check = os.path.abspath(segtest.labDir + '\\' + c)
        expect = os.path.abspath('testdata\\segmentation_tests\\expect_results\\LabelledImages\\' + e)
        same = (tf.imread(check) == tf.imread(expect)).all()
        if not same:
            break 
    print(f'Expected label image results? ... {same}')
    for c, e in zip(os.listdir(segtest.segDir), os.listdir('testdata\\segmentation_tests\\expect_results\\SegmentedImages')):
        check = os.path.abspath(segtest.segDir + '\\' + c)
        expect = os.path.abspath('testdata\\segmentation_tests\\expect_results\\SegmentedImages\\' + e)
        same = (tf.imread(check) == tf.imread(expect)).all()
        if not same:
            break
    print(f'Expected segmented image results? ... {same}')
    for f in os.listdir(segtest.segDir):
        os.remove(os.path.abspath(segtest.segDir + '\\' + f))
    for f in os.listdir(segtest.labDir):
        os.remove(os.path.abspath(segtest.labDir + '\\' + f))
    os.rmdir(segtest.segDir)
    os.rmdir(segtest.labDir)
# end main

