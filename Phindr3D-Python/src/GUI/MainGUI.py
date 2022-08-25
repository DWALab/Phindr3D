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

from .external_windows import *
from .analysis_scripts import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
import PIL.Image
import sys
import random
from scipy.stats.mstats import mquantiles
from .windows.plot_functions import *
from .windows.helperclasses import *
from ..PhindConfig.PhindConfig import TileInfo

from scipy.spatial import distance as dist
try:
    from ..VoxelGroups.VoxelGroups import *
    from ..Clustering.Clustering import *
    from ..Training.Training import *
except ImportError:
    from src.VoxelGroups.VoxelGroups import *
    from src.Clustering.Clustering import *
    from src.Training.Training import *

Generator = Generator()

class MainGUI(QWidget, external_windows):
    """Defines the main GUI window of Phindr3D"""

    def __init__(self):
        """MainGUI constructor"""
        QMainWindow.__init__(self)
        super(MainGUI, self).__init__()
        self.training = Training()
        self.metadata = Metadata(Generator)
        self.voxelGroups = VoxelGroups(self.metadata)
        self.trainbycondition = False # modifiable in paramWindow, but not sure where this is used?
        # self.clustering = Clustering() #dont need this, clustering occurs in the view results parts and the clustering object isnt relevant.
        self.setWindowTitle("Phindr3D")
        self.rgb_img=0
        self.img_ind=1
        #Default color values for image plot
        keys, values = zip(*mcolors.CSS4_COLORS.items())
        values=[values[x] for x, y in enumerate(keys) if 'white' not in y]
        self.color = [(0, 0.45, 0.74),(0.85, 0.33, 0.1), (0.93, 0.69, 0.13)]
        self.ch_len=1
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignBottom)
        # All widgets initialized here, to be placed in their proper section of GUI
        loadmeta = QPushButton("Load MetaData")
        setvoxel = QPushButton("Set Voxel Parameters")
        sv = QCheckBox("SV")
        mv = QCheckBox("MV")
        adjust_thresh = QLabel("Adjust Image Threshold")
        threshbar = QSlider(Qt.Horizontal)
        threshbar.setMaximum(100)
        setcolors = QPushButton("Set Channel Colors")
        slicescroll = QLabel("Slice Scroller")
        slicescrollbar = QSlider(Qt.Horizontal)
        slicescrollbar.setMinimum(0)
        slicescrollbar.setPageStep(1)
        slicescrollbar.setSingleStep(1)
        previmage = QPushButton("Prev Image")
        nextimage = QPushButton("Next Image")
        phind = QPushButton("Phind")
        # Button behaviour defined here
        def metadataError(buttonPressed):
            if not self.metadata.GetMetadataFilename():
                alert = self.buildErrorWindow("Metadata not found!!", QMessageBox.Critical)
                alert.exec()
            elif buttonPressed == "Set Voxel Parameters":
                try:
                    tileInfo = self.metadata.theTileInfo
                    supercoords = (tileInfo.tileX, tileInfo.tileY, tileInfo.tileZ)
                    megacoords = (tileInfo.megaVoxelTileX, tileInfo.megaVoxelTileY, tileInfo.megaVoxelTileZ)
                    winp = self.buildParamWindow(supercoords, self.voxelGroups.numSuperVoxelBins, megacoords,
                                                 self.voxelGroups.numMegaVoxelBins, self.voxelGroups.numVoxelBins,
                                                 self.metadata.randTrainingFields, self.metadata.countBackground,
                                                 self.metadata.intensityNormPerTreatment, self.trainbycondition)
                    winp.show()
                    winp.exec()
                    if winp.done: # when done is pressed (and successful), update all params
                        self.metadata.theTileInfo.tileX = winp.superx
                        self.metadata.theTileInfo.tileY = winp.supery
                        self.metadata.theTileInfo.tileZ = winp.superz
                        self.voxelGroups.numSuperVoxelBins = winp.svcategories
                        self.metadata.theTileInfo.megaVoxelTileX = winp.megax
                        self.metadata.theTileInfo.megaVoxelTileY = winp.megay
                        self.metadata.theTileInfo.megaVoxelTileZ = winp.megaz
                        self.voxelGroups.numMegaVoxelBins = winp.mvcategories
                        self.voxelGroups.numVoxelBins = winp.voxelnum
                        self.metadata.randTrainingFields = winp.trainingnum
                        self.metadata.countBackground = winp.bg
                        self.metadata.intensityNormPerTreatment = winp.norm
                        self.trainbycondition = winp.conditiontrain
                        # after updating parameters, what needs to be done?
                        self.voxelGroups.updateImages()
                        self.metadata.computeImageParameters()
                        self.thresh = self.metadata.intensityThresholdValues
                        self.bounds = [self.metadata.lowerbound, self.metadata.upperbound]
                        threshbar.blockSignals(True)
                        threshbar.setValue(int(PhindConfig().intensityThresholdTuningFactor * 100))
                        threshbar.blockSignals(False)
                        self.img_display(slicescrollbar, img_plot, sv, mv, values, self.img_ind, imgwindow)
                except Exception as e:
                    print(e)

            elif buttonPressed == "Set Channel Colors":
                color = QColorDialog.getColor()
                return color
            elif buttonPressed == "Image Go":
                errortext = "Image Out of Range"
                alert = self.buildErrorWindow(errortext, QMessageBox.Critical)
                alert.exec()
            elif buttonPressed == "Phind":
                try:
                    self.phindButtonAction()
                except Exception as e:
                    print(e)

        def exportError():
            if not self.metadata.GetMetadataFilename():
                alert = self.buildErrorWindow("No variables to export!!", QMessageBox.Critical)
                alert.exec()

        def loadMetadata(self, sv, mv, threshbar, slicescrollbar, img_plot, color, values, imagenav):
            filename, dump = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
            if os.path.exists(filename):
                # When meta data is loaded, using the loaded data, change the data for image viewing
                # Consider adding another class to store all of the data (GUIDATA in MATLab?)
                try:
                    self.metadata.loadMetadataFile(filename)
                    # If the file loaded correctly, proceed to calculating thresholds, scale factors, etc.
                    threshbar.blockSignals(True)
                    slicescrollbar.blockSignals(True)
                    threshbar.setValue(0)
                    slicescrollbar.setValue(0)
                    self.img_ind=1
                    imagenav.setText("1")
                    self.metadata.computeImageParameters()
                    self.thresh=self.metadata.intensityThresholdValues
                    self.bounds=[self.metadata.lowerbound, self.metadata.upperbound]
                    threshbar.setValue(int(PhindConfig().intensityThresholdTuningFactor*100))
                    threshbar.blockSignals(False)
                    slicescrollbar.blockSignals(False)
                    issue=self.img_display(slicescrollbar, img_plot, sv, mv, values, self.img_ind, imgwindow)
                    # Update values of GUI widgets
                    if not issue:
                        alert = self.buildErrorWindow("Metadata Extraction Completed.", QMessageBox.Information, "Notice")
                        alert.exec()
                except MissingChannelStackError:
                    errortext = "Metadata Extraction Failed: Channel/Stack/ImageID column(s) missing and/or invalid."
                    alert = self.buildErrorWindow(errortext, QMessageBox.Critical)
                    alert.exec()
                except FileNotFoundError:
                    errortext = "Metadata Extraction Failed: Metadata file does not exist."
                    alert = self.buildErrorWindow(errortext, QMessageBox.Critical)
                    alert.exec()
                except InvalidImageError:
                    errortext = "Metadata Extraction Failed: Invalid Image type (must be grayscale)."
                    alert = self.buildErrorWindow(errortext, QMessageBox.Critical)
                    alert.exec()
                except Exception as e:
                    print(e)
                    return
            else:
                load_metadata_win = self.buildErrorWindow("Select Valid Metadatafile (.txt)", QMessageBox.Critical)
                load_metadata_win.show()
                load_metadata_win.exec()
                # When meta data is loaded, using the loaded data, change the data for image viewing
                # Consider adding another class to store all of the data (GUIDATA in MATLab?)
        # end loadMetadata

        # metadataError will check if there is metadata. If there is not, create error message.
        # Otherwise, execute button behaviour, depending on button (pass extra parameter to
        # distinguish which button was pressed into metadataError()?)

        def colorpicker():
            if not self.metadata.GetMetadataFilename():
                metadataError("Set Channel Colors")
            else:
                prev_color=self.color[:]
                win_color=colorchannelWindow(self.ch_len, self.color, "Color Channel Picker", "Channels", ['Channel_' + str(i) for i in range(1,self.ch_len+1)])
                self.color=win_color.color
                if np.array_equal(prev_color, self.color)==False:
                    self.img_display(slicescrollbar, img_plot, sv, mv, values, self.img_ind, imgwindow, threshbar.value()/100)

        # Declaring menu actions, to be placed in their proper section of the menubar
        menubar = QMenuBar()
        file = menubar.addMenu("File")
        imp = file.addMenu("Import")
        impsession = imp.addAction("Session")
        impparameters = imp.addAction("Parameters")
        exp = file.addMenu("Export")
        expsessions = exp.addAction("Session")
        expparameters = exp.addAction("Parameters")
        menuexit = file.addAction("Exit")

        metadata = menubar.addMenu("Metadata")
        createmetadata = metadata.addAction("Create Metafile")
        loadmetadata = metadata.addAction("Load Metadata")

        imagetab = menubar.addMenu("Image")
        imagetabnext = imagetab.addAction("Next Image")
        imagetabcolors = imagetab.addAction("Set Channel Colors")

        viewresults = menubar.addAction("View Results")

        about = menubar.addAction("About")

        segmentation = menubar.addAction("Organoid Segmentation App")

        # Testing purposes
        test = menubar.addMenu("Test")
        switchmeta = test.addAction("Switch Metadata")
        switchmeta.setCheckable(True)

        # Menu actions defined here
        def extractMetadata():
            winz = self.buildExtractWindow()
            winz.show()
            winz.exec()

        def viewResults():
            winc = self.buildResultsWindow(self.color, metadata)
            winc.show()
            winc.exec()

        def organoidSegmentation():
            try:
                wino = self.buildSegmentationWindow(self.metadata)
                wino.show()
                wino.exec()
            except Exception as e:
                print(e)

        # Function purely for testing purposes, this function will switch 'foundMetadata' to true or false
        def testMetadata():
            pixels = PixelImage()
            superVoxels = SuperVoxelImage()
            megaVoxels = MegaVoxelImage()
            try:
                pixels.getPixelBinCenters(self.metadata, self.training)
                print(pixels.pixelBinCenters)
                superVoxels.getSuperVoxelBinCenters(self.metadata, self.training, pixels)
                print(superVoxels.superVoxelBinCenters)
                megaVoxels.getMegaVoxelBinCenters(self.metadata, self.training, pixels, superVoxels)
                print(megaVoxels.megaVoxelBinCenters)
            except Exception as e:
                print(e)

        createmetadata.triggered.connect(extractMetadata)
        viewresults.triggered.connect(viewResults)
        imagetabnext.triggered.connect(metadataError)
        imagetabcolors.triggered.connect(metadataError)
        expsessions.triggered.connect(exportError)
        expparameters.triggered.connect(exportError)
        about.triggered.connect(self.aboutAlert)
        segmentation.triggered.connect(organoidSegmentation)
        loadmetadata.triggered.connect(lambda: loadMetadata(self, sv, mv, threshbar, slicescrollbar, img_plot, self.color, values, imagenav))
        menuexit.triggered.connect(self.close)
        imagetabnext.triggered.connect(lambda:  self.img_scroll(1, slicescrollbar, threshbar.value()/100, img_plot, sv, mv, values, imagenav, imgwindow) if self.metadata.GetMetadataFilename() else metadataError("Next Image"))
        imagetabcolors.triggered.connect(lambda: colorpicker() if self.metadata.GetMetadataFilename() else metadataError("Color Channel"))

        switchmeta.triggered.connect(testMetadata)
        # Creating and formatting menubar
        layout.setMenuBar(menubar)

        # create analysis parameters box (top left box)
        analysisparam = QGroupBox("Analysis Parameters")
        grid = QGridLayout()
        grid.setVerticalSpacing(20)
        grid.addWidget(loadmeta, 0, 0, 1, 2)
        grid.addWidget(setvoxel, 1, 0, 1, 2)
        grid.addWidget(sv, 2, 0)
        grid.addWidget(mv, 2, 1)
        grid.addWidget(adjust_thresh, 3, 0, 1, 2)
        grid.addWidget(threshbar, 4, 0, 1, 2)
        analysisparam.setLayout(grid)
        layout.addWidget(analysisparam, 1, 0)

        # create image viewing parameters box (bottom left box)
        imageparam = QGroupBox("Image Viewing Parameters")
        imageparam.setAlignment(1)
        vertical = QFormLayout()
        vertical.addRow(setcolors)
        vertical.addRow(slicescroll)
        vertical.addRow(slicescrollbar)
        image_selection = QHBoxLayout()
        image_selection.addWidget(previmage)
        image_selection.addWidget(nextimage)
        vertical.addRow(image_selection)
        imagenav = QLineEdit()
        imagenav.setValidator(QIntValidator())
        imagego = QPushButton("Image Go")

        imagego.clicked.connect(lambda: self.img_scroll(int(imagenav.text())-self.img_ind, slicescrollbar, threshbar.value()/100, img_plot, sv, mv, values, imagenav, imgwindow) if self.metadata.GetMetadataFilename() else metadataError("Image Go"))
        imageselect = QHBoxLayout()
        imageselect.addWidget(imagenav)
        imageselect.addWidget(imagego)
        vertical.addRow(imageselect)
        imageparam.setLayout(vertical)
        layout.addWidget(imageparam, 2, 0)

        imageparam.setFixedSize(imageparam.minimumSizeHint())
        analysisparam.setFixedSize(analysisparam.minimumSizeHint())
        analysisparam.setFixedWidth(imageparam.minimumWidth())

        # Phind button
        layout.addWidget(phind, 3, 0, Qt.AlignCenter)

        # initialize image plot and layout
        imgwindow = QGroupBox()
        imgwindow.setFlat(True)

        matplotlib.use('Qt5Agg')

        img_plot = MplCanvas(self, width=10, height=10, dpi=300, projection="2d") #inches=pixel*0.0104166667
        img_plot.axes.imshow(np.zeros((2000,2000)), cmap = mcolors.ListedColormap("black"))
        img_plot.axes.axis('off')
        img_plot.fig.set_facecolor("black")
        imagelayout = QVBoxLayout()
        imagelayout.addWidget(img_plot)
        imgwindow.setLayout(imagelayout)
        imgwindow.setFixedSize(450, 450)
        layout.addWidget(imgwindow, 1, 1, 3, 1)
        img_plot.axes.set_aspect("auto")
        img_plot.axes.set_position([0, 0, 1, 1])
        self.setLayout(layout)

        #mainGUI buttons clicked
        setvoxel.clicked.connect(lambda: metadataError("Set Voxel Parameters"))
        loadmeta.clicked.connect(lambda: loadMetadata(self, sv, mv, threshbar, slicescrollbar, img_plot, self.color, values, imagenav))
        nextimage.clicked.connect(lambda:  self.img_scroll(1, slicescrollbar, threshbar.value()/100, img_plot, sv, mv, values, imagenav, imgwindow) if self.metadata.GetMetadataFilename() else metadataError("Next Image"))
        previmage.clicked.connect(lambda:  self.img_scroll(-1, slicescrollbar, threshbar.value()/100, img_plot, sv, mv, values, imagenav, imgwindow) if self.img_ind>1 else None)
        setcolors.clicked.connect(lambda: colorpicker() if self.metadata.GetMetadataFilename() else metadataError("Color Channel"))
        slicescrollbar.valueChanged.connect(lambda: self.img_display(slicescrollbar, img_plot, sv, mv, values, self.img_ind, imgwindow, threshbar.value()/100) if self.metadata.GetMetadataFilename() else metadataError("Slice Scroll"))
        sv.stateChanged.connect(lambda : self.overlay_display(img_plot, self.metadata.theTileInfo, sv, mv, 'SV') if self.metadata.GetMetadataFilename() else metadataError("SV"))
        mv.stateChanged.connect(lambda : self.overlay_display(img_plot, self.metadata.theTileInfo, mv, sv, 'MV') if self.metadata.GetMetadataFilename() else metadataError("MV"))
        phind.clicked.connect(lambda: metadataError("Phind"))
        threshbar.valueChanged.connect(lambda: self.img_display(slicescrollbar, img_plot, sv, mv, values, self.img_ind, imgwindow, threshbar.value()/100) if self.metadata.GetMetadataFilename() else metadataError("Adjust Image Threshold"))
    def img_scroll(self, val, slicescrollbar, thresh, img_plot, sv, mv, values, imagenav, imagewindow):
        #next image/prev image
        img_id=self.img_ind+val
        slicescrollbar.setValue(0)
        issue=self.img_display(slicescrollbar, img_plot, sv, mv, values, img_id, imagewindow, thresh)
        if not issue:
            self.img_ind=self.img_ind+val
        imagenav.setText(str(self.img_ind))
    #draws image layers
    def overlay_display(self, img_plot, params, checkbox_cur, checkbox_prev, type):
        if self.metadata.GetMetadataFilename():

            #re-plot image channel as bottom layer
            img_plot.axes.clear()
            img_plot.axes.imshow(self.rgb_img)
            img_plot.axes.axis('off')
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            if checkbox_cur.isChecked():
                #plot SV/MV GRID
                img_grid= np.full((self.rgb_img.shape[0], self.rgb_img.shape[1], 4), (0.0, 0.0, 0.0, 0.0))
                overlay=DataFunctions.getImageWithSVMVOverlay(img_grid, params, type)
                cmap=[[0,0,0,0],[255,255,255,1]]
                cmap = matplotlib.colors.LinearSegmentedColormap.from_list('map_white', cmap)
                img_plot.axes.imshow(overlay, zorder=5, cmap=cmap, interpolation=None)
            img_plot.draw()
    #draw superimposed image channels
    def img_display(self, slicescrollbar, img_plot, sv, mv, values, img_id, imgwindow, prob=PhindConfig().intensityThresholdTuningFactor):

        if self.metadata.GetMetadataFilename():
            #extract image details from metadata
            data = pd.read_csv(self.metadata.GetMetadataFilename(), sep="\t")
            self.ch_len = (list(np.char.find(list(data.columns), 'Channel_')).count(0))
            #get image index of previous stack
            prev=data[data["ImageID"] == img_id-1]["Channel_1"]
            if prev.size>1:
                prev=prev.index[-1]+1
            else:
                prev=0
            #get size of current stack
            stack_size=data[data["ImageID"] == img_id]["Channel_1"].size
            if stack_size==0:
                imgID_win = self.buildErrorWindow("ImageID out of range", QMessageBox.Critical)
                imgID_win.show()
                imgID_win.exec()
                return(True)
            id=slicescrollbar.value()+prev
            slicescrollbar.setMaximum(stack_size-1)
            #add/remove colour channels if not default of 3 channels
            if self.ch_len>3 and len(self.color)<self.ch_len:
                count=self.ch_len-len(self.color)
                while count>0:
                    new_color=mcolors.to_rgb(values[random.sample(range(0,len(values)-1), 1)[0]])
                    if (new_color in self.color)==False:
                        self.color.append(new_color)
                        count=count - 1
            elif self.ch_len<2 and len(self.color)>self.ch_len:
                self.color=self.color[:-(len(self.color)-self.ch_len)]
            #check if treatment column and treatmentnormspecified
            treat=""
            bound=self.bounds[:]
            if len(np.shape(bound))>2:
                bound=treatment_bounds(self, data, self.bounds, id)
                if not bound:
                    return(True)
            #initialize array as image size with # channels
            rgb_img = PIL.Image.open(data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[id]).size
            rgb_img = np.zeros((self.ch_len, rgb_img[1], rgb_img[0], 3))
            threshold=mquantiles(self.thresh, prob, alphap=0.5, betap=0.5, axis=0)
            self.rgb_img=merge_channels(data, rgb_img, self.ch_len, id, self.color, 0, False, bound, threshold)
            #plot combined channels
            img_plot.axes.clear()
            imgwindow.setFixedWidth(floor(450* self.rgb_img.shape[1] / max(self.rgb_img.shape[1], self.rgb_img.shape[0])))
            imgwindow.setFixedHeight(floor(450* self.rgb_img.shape[0] / max(self.rgb_img.shape[1], self.rgb_img.shape[0])))
            img_plot.axes.imshow(self.rgb_img)
            img_plot.axes.axis('off')
            img_plot.draw()

            #add thresholds/bounds to metadatafile
            data.drop(data.filter(regex="Unname"),axis=1, inplace=True)
            if 'bounds' not in data.columns and 'intensity_thresholds' not in data.columns:
                data.insert(loc=int(np.where(data.columns == 'ImageID')[0]), column='bounds', value=np.repeat([self.bounds], data.shape[0], axis=0).tolist())
                data.insert(loc=int(np.where(data.columns == 'ImageID')[0]), column='intensity_thresholds', value=np.repeat([mquantiles(self.thresh, 0, alphap=0.5, betap=0.5, axis=0)], data.shape[0], axis=0).tolist())
            else:
                data['bounds']= np.repeat([self.bounds], data.shape[0], axis=0).tolist()
                data['intensity_thresholds']= np.repeat([mquantiles(self.thresh, 0, alphap=0.5, betap=0.5, axis=0)], data.shape[0], axis=0).tolist()
            data.to_csv(data['MetadataFile'].str.replace(r'\\', '/', regex=True).iloc[0], sep='\t', index=False)
            #sv/mv overlay removed when new image
            sv.setChecked(False)
            mv.setChecked(False)
        return(False)
    # end img_display

    def phindButtonAction(self):
        """Actions performed when the Phind button is pressed and metadata has been loaded"""
        if self.metadata.GetMetadataFilename():
            #get output dir:
            savefile, dump = QFileDialog.getSaveFileName(self, 'Phindr3D Results', '', 'Text file (*.txt)')
            self.metadata.computeImageParameters()
            self.training.randFieldID = self.metadata.trainingSet

            if len(savefile) > 0:
                if self.voxelGroups.action(savefile, self.training):
                    message = f'All Done!\n\nResults saved at:\n{savefile}'
                    alert = self.buildErrorWindow(message, QMessageBox.Information, "Notice")
                    alert.exec()
                else:
                    # error
                    print('something went wrong.')
                    print("voxel grouping failed")
        else:
            # do nothing? display error window?
            pass
    # end phindButtonAction

    def buildErrorWindow(self, errormessage, icon, errortitle="ErrorDialog"):
        alert = QMessageBox()
        alert.setWindowTitle(errortitle)
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def aboutAlert(self):
        alert = QMessageBox()
        alert.setText("talk about the program")
        alert.setWindowTitle("About")
        alert.exec()

    def closeEvent(self, event):
        #print("closed all windows")
        for window in QApplication.topLevelWidgets():
            window.close()

def run_mainGUI():
    """Show the window and run the application exec method to start the GUI"""
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    app.exec()

class InvalidImageError(Exception):
    pass

# end class MainGUI