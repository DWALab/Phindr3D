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
from PIL import Image
import sys
import random


class MainGUI(QWidget, external_windows):
    """Defines the main GUI window of Phindr3D"""

    def __init__(self):
        """MainGUI constructor"""
        QMainWindow.__init__(self)
        super(MainGUI, self).__init__()
        self.metadata_file=False
        self.setWindowTitle("Phindr3D")
        self.image_grid=0
        self.rgb_img=[]

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignBottom)

        # All widgets initialized here, to be placed in their proper section of GUI
        loadmeta = QPushButton("Load MetaData")
        setvoxel = QPushButton("Set Voxel Parameters")
        sv = QCheckBox("SV")
        mv = QCheckBox("MV")
        adjust = QLabel("Adjust Image Threshold")
        adjustbar = QSlider(Qt.Horizontal)
        setcolors = QPushButton("Set Channel Colors")
        slicescroll = QLabel("Slice Scroller")
        slicescrollbar = QSlider(Qt.Horizontal)
        slicescrollbar.setMinimum(0)
        previmage = QPushButton("Prev Image")
        nextimage = QPushButton("Next Image")
        phind = QPushButton("Phind")
        # Button behaviour defined here
        def metadataError(buttonPressed):
            if not self.metadata_file:
                alert = self.buildErrorWindow("Metadata not found!!", QMessageBox.Critical)
                alert.exec()
            elif buttonPressed == "Set Voxel Parameters":
                winp = self.buildParamWindow()
                winp.show()
                winp.exec()

        def exportError():
            if not self.metadata_file:
                alert = self.buildErrorWindow("No variables to export!!", QMessageBox.Critical)
                alert.exec()

        def loadMetadata(self, sv, mv, adjustbar, slicescrollbar, img_plot, color, values):
            filename, dump = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
            if filename != '':
                self.metadata_file=filename
                print(self.metadata_file)
                adjustbar.setValue(0)
                slicescrollbar.setValue(0)
                self.img_display(slicescrollbar, img_plot, sv, mv, color, values)
            else:
                load_metadata_win = self.buildErrorWindow("Select Valid Metadatafile (.txt)", QMessageBox.Critical)
                load_metadata_win.exec()
                # When meta data is loaded, using the loaded data, change the data for image viewing
                # Consider adding another class to store all of the data (GUIDATA in MATLab?)
        # metadataError will check if there is metadata. If there is not, create error message.
        # Otherwise, execute button behaviour, depending on button (pass extra parameter to
        # distinguish which button was pressed into metadataError()?)

        def colorpicker():
            if not self.metadata_file:
                metadataError("Set Channel Colors")
            else:
                prev_color=self.color[:]
                colorchannelWindow(self.ch_len, self.color)
                if np.array_equal(prev_color, self.color)==False:
                    self.img_display(slicescrollbar, img_plot, sv, mv, self.color, values)

        # Declaring menu actions, to be placed in their proper section of the menubar
        menubar = QMenuBar()

        file = menubar.addMenu("File")
        imp = file.addMenu("Import")
        impsession = imp.addAction("Session")
        impparameters = imp.addAction("Parameters")
        exp = file.addMenu("Export")
        expsessions = exp.addAction("Session")
        expparameters = exp.addAction("Parameters")

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
            winc = self.buildResultsWindow()
            winc.show()
            winc.exec()

        def organoidSegmentation():
            wino = self.buildSegmentationWindow()
            wino.show()
            wino.exec()

        # Function purely for testing purposes, this function will switch 'foundMetadata' to true or false
        def testMetadata():
            self.metadata_file= not self.metadata_file

        createmetadata.triggered.connect(extractMetadata)
        viewresults.triggered.connect(viewResults)
        imagetabnext.triggered.connect(metadataError)
        imagetabcolors.triggered.connect(metadataError)
        expsessions.triggered.connect(exportError)
        expparameters.triggered.connect(exportError)
        about.triggered.connect(self.aboutAlert)
        segmentation.triggered.connect(organoidSegmentation)

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
        grid.addWidget(adjust, 3, 0, 1, 2)
        grid.addWidget(adjustbar, 4, 0, 1, 2)
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

        img_plot = MplCanvas(self, width=25, height=25, dpi=300, projection="2d") #inches=pixel*0.0104166667
        img_plot.axes.imshow(np.zeros((2000,2000)), cmap = mcolors.ListedColormap("black"))
        img_plot.fig.set_facecolor("black")
        imagelayout = QVBoxLayout()
        imagelayout.addWidget(img_plot)
        imgwindow.setLayout(imagelayout)
        imgwindow.setFixedSize(450, 450)
        layout.addWidget(imgwindow, 1, 1, 3, 1)
        img_plot.axes.set_aspect("auto")
        img_plot.axes.set_position([0, 0, 1, 1])
        self.setLayout(layout)
        #Default color values for image plot
        keys, values = zip(*mcolors.CSS4_COLORS.items())
        self.color = [mcolors.to_rgb(values[keys.index('red')]), mcolors.to_rgb(values[keys.index('green')]),
                 mcolors.to_rgb(values[keys.index('blue')])]
        self.ch_len=1

        #mainGUI buttons clicked
        setvoxel.clicked.connect(lambda: metadataError("Set Voxel Parameters"))
        adjustbar.valueChanged.connect(lambda: metadataError("Adjust Image Threshold"))
        loadmeta.clicked.connect(lambda: loadMetadata(self, sv, mv, adjustbar, slicescrollbar, img_plot, self.color, values))
        nextimage.clicked.connect(lambda: slicescrollbar.setValue(int(slicescrollbar.value())+1) if self.metadata_file else metadataError("Next Image"))
        previmage.clicked.connect(lambda: slicescrollbar.setValue(int(slicescrollbar.value())-1) if int(slicescrollbar.value())>0 else None)
        setcolors.clicked.connect(lambda: colorpicker() if self.metadata_file else metadataError("Color Channel"))
        slicescrollbar.valueChanged.connect(lambda: self.img_display(slicescrollbar, img_plot, sv, mv, self.color, values) if self.metadata_file else metadataError("Slice Scroll"))

        #TEMPORARY PARAMS! until set voxel parameters is finished...
        class params(object):
                tileX = 10
                tileY = 10
                megaVoxelTileX = 5
                megaVoxelTileY = 5
        param=params()
        sv.stateChanged.connect(lambda : self.overlay_display(img_plot, self.image_grid, param, sv, mv, 'SV') if self. metadata_file else metadataError("SV"))
        mv.stateChanged.connect(lambda : self.overlay_display(img_plot, self.image_grid, param, mv, sv, 'MV') if self. metadata_file else metadataError("MV"))
        phind.clicked.connect(lambda: metadataError("Phind"))
    #draws image layers
    def overlay_display(self, img_plot, img_grid, params, checkbox_cur, checkbox_prev, type):

        if self.metadata_file:
            #re-plot image channel as bottom layer
            img_plot.axes.clear()
            img_plot.axes.imshow(self.rgb_img)
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            if checkbox_cur.isChecked():
                #plot SV/MV GRID
                overlay=getImageWithSVMVOverlay(img_grid, params, type)
                cmap=[[0,0,0,0],[255,255,255,1]]
                cmap = matplotlib.colors.LinearSegmentedColormap.from_list('map_white', cmap)
                img_plot.axes.imshow(overlay, zorder=5, cmap=cmap, interpolation=None)
                self.image_grid = np.full((self.rgb_img.shape[0], self.rgb_img.shape[1], 4), (0.0, 0.0, 0.0, 0.0))
            img_plot.draw()
    #draw superimposed image channels
    def img_display(self, slicescrollbar, img_plot, sv, mv, color, values):

        if self.metadata_file:
            #extract image details from metadata
            data = pd.read_csv(self.metadata_file, sep="\t")
            self.ch_len = (list(np.char.find(list(data.columns), 'Channel_')).count(0))
            slicescrollbar.setMaximum((data.shape[0]-1)/(self.ch_len-1))
            print(data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[slicescrollbar.value()])

            #add/remove colour channels if not default of 3 channels
            if self.ch_len>3 and len(self.color)<self.ch_len:
                count=self.ch_len-len(self.color)
                while count>0:
                    new_color=mcolors.to_rgb(values[random.sample(range(0,len(values)-1), 1)[0]])
                    if (new_color in self.color)==False:
                        self.color.append(new_color)
                        count=count - 1
            elif self.ch_len<2 and len(color)>self.ch_len:
                color=color[:-(len(color)-self.ch_len)]

            #initialize array as image size with # channels
            rgb_img = Image.open(data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[slicescrollbar.value()]).size
            rgb_img = np.empty((rgb_img[0], rgb_img[1], 3, self.ch_len))

            #threshold/colour each image channel
            for ind, rgb_color in zip(range(slicescrollbar.value(), slicescrollbar.value()+ self.ch_len), color):
                ch_num=str(ind-slicescrollbar.value()+1)
                data['Channel_'+ch_num]=data['Channel_'+ch_num].str.replace(r'\\', '/', regex=True)
                cur_img = np.array(Image.open(data['Channel_'+ch_num].iloc[ind]))
                threshold=getImageThreshold(cur_img)
                cur_img[cur_img<=threshold]=0
                cur_img= np.dstack((cur_img, cur_img, cur_img))
                rgb_img[:, :, :, int(ch_num) - 1] = cur_img*rgb_color

            #compute average and norm to mix colours
            divisor=np.sum(rgb_img!= 0, axis=-1)
            tot = np.sum(rgb_img, axis=-1)
            rgb_img=np.divide(tot, divisor, out=np.zeros_like(tot), where=divisor != 0)
            max_rng=[np.max(rgb_img[:,:,i]) if np.max(rgb_img[:,:,i])>0 else 1 for i in range(self.ch_len)]
            self.rgb_img = np.divide(rgb_img,max_rng)

            #plot combined channels
            img_plot.axes.clear()
            img_plot.axes.imshow(self.rgb_img)
            img_plot.draw()

            self.image_grid=np.full((self.rgb_img.shape[0], self.rgb_img.shape[1], 4), (0.0,0.0,0.0,0.0))

            #sv/mv overlay removed when new image
            sv.setChecked(False)
            mv.setChecked(False)

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def aboutAlert(self):
        alert = QMessageBox()
        alert.setText("talk about the program")
        alert.setWindowTitle("About")
        alert.exec()

    def closeEvent(self, event):
        print("closed all windows")
        for window in QApplication.topLevelWidgets():
            window.close()

def run_mainGUI():
    """Show the window and run the application exec method to start the GUI"""
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    app.exec()

# end class MainGUI