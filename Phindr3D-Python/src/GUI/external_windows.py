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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ..Data import *
import matplotlib
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
import pandas as pd
from scipy.spatial import distance
import numpy as np
from PIL import Image
import sys
import os


#Matplotlib Figure
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=5, dpi=100, projection="3d"):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if projection=="3d":
            self.axes = self.fig.add_subplot(111, projection=projection)
        else:
            self.axes = self.fig.add_subplot(111, projection=None)
        super(MplCanvas, self).__init__(self.fig)

#imported matplotlib toolbar. Only use desired functions.
class NavigationToolbar(NavigationToolbar):
    NavigationToolbar.toolitems = (
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Customize', 'Edit axis, curve and image parameters', 'qt4_editor_options', 'edit_parameters'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure')
    )

#Callback will open image associated with data point
class pick_onclick():
    def __init__(self, main_plot, projection, x, y, z):
        self.main_plot=main_plot
        self.projection=projection
        self.x=x
        self.y=y
        self.z=z
        class buildImageViewer(QWidget):
            def __init__(self):
                super().__init__()
                self.resize(1000, 1000)
                self.setWindowTitle("ImageViewer")
                grid = QGridLayout()

                #info layout
                info_box = QVBoxLayout()
                file_info=QLineEdit("FileName:\n")
                file_info.setAlignment(Qt.AlignTop)
                file_info.setReadOnly(True)
                ch_info=QLineEdit("Channels\n")
                ch_info.setAlignment(Qt.AlignTop)
                ch_info.setReadOnly(True)
                file_info.setFixedWidth(200)
                file_info.setMinimumHeight(350)
                ch_info.setFixedWidth(200)
                ch_info.setMinimumHeight(350)
                info_box.addStretch()
                info_box.addWidget(file_info)
                info_box.addWidget(ch_info)
                info_box.addStretch()

                #projection layout
                pjt_box = QGroupBox("Projection Type")
                pjt_type= QHBoxLayout()
                slice_btn = QRadioButton("Slice")
                mit_btn = QRadioButton("MIT")
                montage_btn = QRadioButton("Montage")
                pjt_type.addStretch()
                pjt_type.addWidget(slice_btn)
                pjt_type.addWidget(mit_btn)
                pjt_type.addWidget(montage_btn)
                pjt_type.addStretch()
                pjt_type.setSpacing(100)
                pjt_box.setLayout(pjt_type)

                #image plot layout
                matplotlib.use('Qt5Agg')

                x = []
                y = []
                # if !self.foundMetadata:  #x and y coordinates from super/megavoxels
                # x=
                # y=
                main_plot = MplCanvas(self, width=12, height=12, dpi=100, projection='2d')
                main_plot.fig.set_facecolor('#f0f0f0')
                main_plot.axes.scatter(x, y)
                main_plot.axes.get_xaxis().set_visible(False)
                main_plot.axes.get_yaxis().set_visible(False)

                # adjustbar layout
                adjustbar = QSlider(Qt.Vertical)
                adjustbar.setFixedWidth(50)
                adjustbar.setStyleSheet(
                    "QSlider::groove:vertical {background-color: #8DE8F6; border: 1px solid;height: 700px;margin: 0px;}"
                    "QSlider::handle:vertical {background-color: #8C8C8C; border: 1px silver; height: 30px; width: 10px; margin: -5px 0px;}")

                #parent layout
                grid.addLayout(info_box, 0, 0)
                grid.addWidget(main_plot, 0, 1)
                grid.addWidget(pjt_box, 1, 1, Qt.AlignCenter)
                grid.addWidget(adjustbar, 0, 2)

                self.setLayout(grid)

        self.winc = buildImageViewer()

    def __call__(self, event):
        if event:
            point_index = int(event.ind)
            #for debugging
            print("X=",self.x[point_index], " Y=", self.y[point_index], " Z=", self.z[point_index], " PointIdx=", point_index)

            plt.figure(1)
            #circle in red selected data point
            self.main_plot.axes.scatter(self.x[point_index], self.y[point_index], self.z[point_index], s=20, facecolor="none", edgecolor='red', alpha=1)
            self.main_plot.draw()
            winc=self.winc
            winc.show()

#zoom in/out fixed xy plane
class fixed_2d():
    def __init__(self, main_plot, sc_plot, projection):
        self.main_plot =main_plot
        self.sc_plot =sc_plot
        self.projection = projection

    def __call__(self, event):

        if event.inaxes is not None:
            if self.projection=="2d":
                if event.button == 'up':
                    self.main_plot.axes.mouse_init()
                    self.main_plot.axes.xaxis.zoom(-1)
                    self.main_plot.axes.yaxis.zoom(-1)
                    self.main_plot.axes.zaxis.zoom(-1)
                if event.button =='down':
                    self.main_plot.axes.xaxis.zoom(1)
                    self.main_plot.axes.yaxis.zoom(1)
                    self.main_plot.axes.zaxis.zoom(-1)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()

class extractWindow(QDialog):
    def __init__(self):
        super(extractWindow, self).__init__()
        largetext = QFont("Arial", 12, 1)
        self.setWindowTitle("Extract Metadata")
        directory = "Image Root Directory"
        samplefilename = "Sample File Name"
        layout = QGridLayout()
        imagerootbox = QTextEdit()
        imagerootbox.setReadOnly(True)
        imagerootbox.setPlaceholderText(directory)
        imagerootbox.setFixedSize(300, 60)
        imagerootbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        imagerootbox.setFont(largetext)

        selectimage = QPushButton("Select Image Directory")
        selectimage.setFixedSize(selectimage.minimumSizeHint())
        selectimage.setFixedHeight(40)

        samplefilebox = QTextEdit()
        samplefilebox.setReadOnly(True)
        samplefilebox.setPlaceholderText(samplefilename)
        samplefilebox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        samplefilebox.setFont(largetext)
        samplefilebox.setFixedSize(450, 30)

        expressionbox = QLineEdit()
        expressionbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        expressionbox.setFont(largetext)
        expressionbox.setFixedSize(450, 30)
        expressionbox.setPlaceholderText("Type Regular Expression Here")

        evaluateexpression = QPushButton("Evaluate Regular Expression")
        evaluateexpression.setFixedSize(evaluateexpression.minimumSizeHint())
        evaluateexpression.setFixedHeight(30)

        outputfilebox = QLineEdit()
        outputfilebox.setAlignment(Qt.AlignCenter)
        outputfilebox.setFont(largetext)
        outputfilebox.setPlaceholderText("Output Metadata File Name")
        outputfilebox.setFixedSize(200, 30)

        createfile = QPushButton("Create File")
        createfile.setFixedSize(createfile.minimumSizeHint())
        createfile.setFixedHeight(30)

        cancel = QPushButton("Cancel")
        cancel.setFixedSize(cancel.minimumSizeHint())
        cancel.setFixedHeight(30)

        # button functions
        def selectImageDir():
            imagedir = QFileDialog.getExistingDirectory()
            if not os.path.exists(imagedir):
                return
            imagerootbox.setText(imagedir)
            # select first '.tif' or '.tiff' file to be sample file
            for file in os.listdir(imagedir):
                if file.endswith('.tiff') or file.endswith('.tif'):
                    samplefilebox.setText(file)
                    break
        def createFile():
            imagedir = imagerootbox.toPlainText()
            regex = expressionbox.text()
            outputname = outputfilebox.text()
            datas = DataFunctions()
            # replace '?<' patterns with '?P<' to make compatible with re.fullmatch function
            # first checks if '?<' corresponds to a '?<=' or '?<!' pattern first before replacing
            # part of Python specific regular expression syntax

            regexlen = regex.__len__()
            for i in range(regexlen):
                if regex[i] == '<':
                    if i > 0:
                        if regex[i - 1] == '?':
                            if i < regexlen - 1:
                                if regex[i + 1] != '!' and regex[i + 1] != '=':
                                    regex = regex[:i] + 'P' + regex[i:]
            try:
                alert = QMessageBox()
                try:
                    if outputname != "":
                        created = datas.createMetadata(imagedir, regex, outputname)
                    else:
                        created = datas.createMetadata(imagedir, regex)
                    if created:
                        alert.setText("Metadata creation success.")
                        alert.setIcon(QMessageBox.Information)
                        alert.setWindowTitle("Notice")
                        self.close()
                    else:
                        alert.setText("Error: No Regex matches found in selected folder.")
                        alert.setIcon(QMessageBox.Critical)
                except MissingChannelStackError:
                    alert.setText("Error: No Channel and/or Stack groups found in regex.")
                    alert.setIcon(QMessageBox.Critical)
                alert.show()
                alert.exec()
            except WindowsError:
                alert = QMessageBox()
                alert.setWindowTitle("Error")
                alert.setText("No such image directory exists.")
                alert.setIcon(QMessageBox.Critical)
                alert.show()
                alert.exec()

        def evalRegex():
            regex = expressionbox.text()
            samplefile = samplefilebox.toPlainText()
            if regex == "" or samplefile == samplefilename:
                return
            datas = DataFunctions()
            regexdict = datas.parseAndCompareRegex(samplefile, regex)
            # for debugging
            if regexdict != None:
                print(regexdict)

        cancel.clicked.connect(self.close)
        selectimage.clicked.connect(selectImageDir)
        createfile.clicked.connect(createFile)
        evaluateexpression.clicked.connect(evalRegex)

        layout.addWidget(imagerootbox, 0, 0, 1, 2)
        layout.addWidget(selectimage, 0, 2, 1, 1)
        layout.addWidget(samplefilebox, 1, 0, 1, 3)
        layout.addWidget(expressionbox, 2, 0, 1, 3)
        layout.addWidget(evaluateexpression, 3, 0, 1, 1)
        layout.addWidget(outputfilebox, 4, 0, 1, 1)
        layout.addWidget(createfile, 4, 1, 1, 1)
        layout.addWidget(cancel, 4, 2, 1, 1)
        layout.setSpacing(10)
        self.setLayout(layout)
        self.setFixedSize(self.minimumSizeHint())

class resultsWindow(QDialog):
    def __init__(self):
        super(resultsWindow, self).__init__()
        self.setWindowTitle("Results")
        self.feature_file=False
        menubar = QMenuBar()
        file = menubar.addMenu("File")
        inputfile = file.addAction("Input Feature File")
        data = menubar.addMenu("Data Analysis")
        classification = data.addMenu("Classification")
        selectclasses = classification.addAction("Select Classes")
        clustering = data.addMenu("Clustering")
        estimate = clustering.addAction("Estimate Clusters")
        setnumber = clustering.addAction("Set Number of Clusters")
        piemaps = clustering.addAction("Pie Maps")
        export = clustering.addAction("Export Cluster Results")
        plotproperties = menubar.addMenu("Plot Properties")
        rotation = plotproperties.addAction("3D Rotation")
        reset_action = QAction("Reset Plot View", self)
        reset_action.triggered.connect(lambda: self.reset_view())
        resetview = plotproperties.addAction(reset_action)

        # menu features go here

        # defining widgets
        box = QGroupBox()
        boxlayout = QGridLayout()
        selectfile = QPushButton("Select Feature File")
        typedropdown = QComboBox()
        typedropdown.addItem("PCA")
        typedropdown.addItem("t-SNE")
        typedropdown.addItem("Sammon")
        twod = QCheckBox("2D")
        threed = QCheckBox("3D")
        dimensionbox = QGroupBox()
        dimensionboxlayout = QHBoxLayout()
        dimensionboxlayout.addWidget(twod)
        dimensionboxlayout.addWidget(threed)
        dimensionbox.setLayout(dimensionboxlayout)
        colordropdown = QComboBox()
        boxlayout.addWidget(selectfile, 0, 0, 3, 1)
        boxlayout.addWidget(QLabel("Plot Type"), 0, 1, 1, 1)
        boxlayout.addWidget(typedropdown, 1, 1, 1, 1)
        boxlayout.addWidget(dimensionbox, 2, 1, 1, 1)
        boxlayout.addWidget(QLabel("Color By"), 0, 2, 1, 1)
        boxlayout.addWidget(colordropdown, 1, 2, 1, 1)
        box.setLayout(boxlayout)
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        # test points. normally empty list x=[], y=[], z=[] #temporary until read in formated super/megavoxel data
        x = [1, 5]
        y = [7, 2]
        z = [0,0]
        # if !self.foundMetadata:  #x and y coordinates from super/megavoxels
        # x=
        # y=
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter(x, y, z, s=10, alpha=1, depthshade=False, picker=True)
        self.main_plot.axes.set_position([0, 0, 1, 1])
        if not x and not y:
            self.main_plot.axes.set_ylim(bottom=0)
            self.main_plot.axes.set_xlim(left=0)
        self.original_xlim=0
        self.original_ylim=0
        if all(np.array(z)==0):
            self.original_zlim=[0, 0.1]

        projection = "2d"  # update from radiobutton
        def axis_limit(sc_plot):
            xlim = sc_plot.axes.get_xlim3d()
            ylim = sc_plot.axes.get_ylim3d()
            lower_lim=min(xlim[0], ylim[0])
            upper_lim=max(xlim[1], ylim[1])
            return(lower_lim, upper_lim)
        def toggle_2d_3d(x, y, z, projection, sc_plot, checkbox_cur, checkbox_prev, dim):
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            check_projection(x, y, z, projection, sc_plot, dim)
        def check_projection(x, y, z, projection, sc_plot, dim):
            if dim == "2d":
                projection=dim
                low, high= axis_limit(sc_plot)
                #for debugging
                #print(low, high)
                self.main_plot.axes.mouse_init()
                self.main_plot.axes.view_init(azim=-90, elev=89)
                if self.original_xlim==0 and self.original_ylim==0 and self.original_zlim==0:
                    self.original_xlim=[low-1, high+1]
                    self.original_ylim=[low - 1, high + 1]
                self.main_plot.axes.set_xlim(low-1, high+1)
                self.main_plot.axes.set_ylim(low-1, high+1)
                self.main_plot.axes.get_zaxis().line.set_linewidth(0)
                self.main_plot.axes.tick_params(axis='z', labelsize=0)
                self.main_plot.axes.set_zlim3d(0,0.1)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()
            elif dim == "3d":
                projection = dim
                self.main_plot.axes.get_zaxis().line.set_linewidth(1)
                self.main_plot.axes.tick_params(axis='z', labelsize=10)
                self.main_plot.fig.canvas.draw()
                self.main_plot.axes.mouse_init()

        # button features go here
        selectfile.clicked.connect(lambda: self.loadFeaturefile())
        twod.toggled.connect(lambda: toggle_2d_3d(x, y, z, projection, sc_plot, twod, threed, "2d"))
        threed.toggled.connect(lambda: toggle_2d_3d(x, y, z, projection, sc_plot, threed, twod, "3d"))
        twod.setChecked(True)
        fixed_camera = fixed_2d(self.main_plot, sc_plot, projection)
        picked=pick_onclick(self.main_plot, projection, x, y, z)
        # matplotlib callback mouse/scroller actions
        rot =self.main_plot.fig.canvas.mpl_connect('scroll_event', fixed_camera)
        self.main_plot.fig.canvas.mpl_connect('pick_event', picked)

        # building layout
        layout = QGridLayout()
        toolbar = NavigationToolbar(self.main_plot, self)

        layout.addWidget(toolbar, 0, 0, 1, 1)
        layout.addWidget(self.main_plot, 1, 0, 1, 1)
        layout.addWidget(box, 2, 0, 1, 1)
        layout.setMenuBar(menubar)
        self.setLayout(layout)
        minsize = self.minimumSizeHint()
        minsize.setHeight(self.minimumSizeHint().height() + 400)
        minsize.setWidth(self.minimumSizeHint().width() + 300)
        self.setFixedSize(minsize)
    def reset_view(self):
        print(self.original_xlim, self.original_ylim, self.original_zlim)
        self.main_plot.axes.set_xlim(self.original_xlim)
        self.main_plot.axes.set_ylim(self.original_ylim)
        self.main_plot.axes.set_zlim3d(self.original_zlim)
        self.main_plot.axes.view_init(azim=-90, elev=89)
        self.main_plot.draw()

    def loadFeaturefile(self):
        filename, dump = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
        if filename != '':
            self.feature_file = filename
            print(self.feature_file)
        else:
            load_featurefile_win = self.buildErrorWindow("Select Valid Feature File (.txt)", QMessageBox.Critical)
            load_featurefile_win.exec()

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert


class paramWindow(QDialog):
    def __init__(self):
        super(paramWindow, self).__init__()
        self.setWindowTitle("Set Parameters")
        winlayout = QGridLayout()

        # super voxel box
        superbox = QGroupBox()
        superbox.setLayout(QGridLayout())
        supersizebox = QGroupBox()
        supersizebox.setLayout(QGridLayout())
        superxin = QLineEdit()
        superyin = QLineEdit()
        superzin = QLineEdit()
        superxin.setFixedWidth(30)
        superyin.setFixedWidth(30)
        superzin.setFixedWidth(30)
        supersizebox.layout().addWidget(superxin, 0, 1, 1, 1)
        supersizebox.layout().addWidget(superyin, 1, 1, 1, 1)
        supersizebox.layout().addWidget(superzin, 2, 1, 1, 1)
        supersizebox.layout().addWidget(QLabel("X"), 0, 0, 1, 1)
        supersizebox.layout().addWidget(QLabel("Y"), 1, 0, 1, 1)
        supersizebox.layout().addWidget(QLabel("Z"), 2, 0, 1, 1)
        supersizebox.setTitle("Size")
        supersizebox.layout().setContentsMargins(20, 10, 20, 20)
        superbox.setTitle("Super Voxel")
        svnum = QLineEdit()
        svnum.setFixedWidth(30)
        superbox.layout().addWidget(svnum, 1, 1, 1, 1)
        superbox.layout().addWidget(QLabel("#SV\n Categories"), 1, 0, 1, 1)
        superbox.layout().addWidget(supersizebox, 0, 0, 1, 2)
        superbox.setFixedWidth(superbox.minimumSizeHint().width() + 20)
        superbox.setFixedHeight(superbox.minimumSizeHint().height() + 20)

        # mega voxel box
        megabox = QGroupBox()
        megabox.setLayout(QGridLayout())
        megasizebox = QGroupBox()
        megasizebox.setLayout(QGridLayout())
        megaxin = QLineEdit()
        megayin = QLineEdit()
        megazin = QLineEdit()
        megaxin.setFixedWidth(30)
        megayin.setFixedWidth(30)
        megazin.setFixedWidth(30)
        megasizebox.layout().addWidget(megaxin, 0, 1, 1, 1)
        megasizebox.layout().addWidget(megayin, 1, 1, 1, 1)
        megasizebox.layout().addWidget(megazin, 2, 1, 1, 1)
        megasizebox.layout().addWidget(QLabel("X"), 0, 0, 1, 1)
        megasizebox.layout().addWidget(QLabel("Y"), 1, 0, 1, 1)
        megasizebox.layout().addWidget(QLabel("Z"), 2, 0, 1, 1)
        megasizebox.setTitle("Size")
        megasizebox.layout().setContentsMargins(20, 10, 20, 20)
        megabox.setTitle("Mega Voxel")
        mvnum = QLineEdit()
        mvnum.setFixedWidth(30)
        megabox.layout().addWidget(mvnum, 1, 1, 1, 1)
        megabox.layout().addWidget(QLabel("#MV\n Categories"), 1, 0, 1, 1)
        megabox.layout().addWidget(megasizebox, 0, 0, 1, 2)
        megabox.setFixedSize(superbox.size())

        # main box
        mainbox = QGroupBox()
        mainbox.setLayout(QGridLayout())
        voxelcategories = QLineEdit()
        voxelcategories.setFixedWidth(30)
        trainingimages = QLineEdit()
        trainingimages.setFixedWidth(30)
        usebackground = QCheckBox("Use Background Voxels for comparing") # text is cutoff, don't know actual line?
        normalise = QCheckBox("Normalise Intesity\n Per Condition")
        trainbycondition = QCheckBox("Train by condition")
        leftdropdown = QComboBox()
        leftdropdown.setEnabled(False)
        rightdropdown = QComboBox()
        rightdropdown.setEnabled(False)
        normalise.clicked.connect(lambda: leftdropdown.setEnabled(not leftdropdown.isEnabled()))
        trainbycondition.clicked.connect(lambda: rightdropdown.setEnabled(not rightdropdown.isEnabled()))

        mainbox.layout().addWidget(QLabel("#Voxel\nCategories"), 0, 0, 1, 1)
        mainbox.layout().addWidget(voxelcategories, 0, 1, 1, 1)
        mainbox.layout().addWidget(QLabel("#Training\nImages"), 0, 3, 1, 1)
        mainbox.layout().addWidget(trainingimages, 0, 4, 1, 1)
        mainbox.layout().addWidget(usebackground, 1, 0, 1, 6)
        mainbox.layout().addWidget(normalise, 2, 0, 1, 3)
        mainbox.layout().addWidget(trainbycondition, 2, 3, 1, 3)
        mainbox.layout().addWidget(leftdropdown, 3, 0, 1, 3)
        mainbox.layout().addWidget(rightdropdown, 3, 3, 1, 3)
        mainbox.setFixedWidth(mainbox.minimumSizeHint().width() + 50)
        mainbox.setFixedHeight(mainbox.minimumSizeHint().height() + 20)

        # reset and done buttons
        reset = QPushButton("Reset")
        done = QPushButton("Done")

        # button behaviours
        def donePressed():
            # When done is pressed, all the inputted values are returned, stored in their place
            # and the window closes
            # Theoretically stored where overall parameters are stored (externally)
            superx = superxin.text()
            supery = superyin.text()
            superz = superzin.text()
            svcategories = svnum.text()
            megax = megaxin.text()
            megay = megayin.text()
            megaz = megazin.text()
            mvcategories = mvnum.text()
            voxelnum = voxelcategories.text()
            trainingnum = trainingimages.text()
            bg = usebackground.isChecked() # For checkboxes, return boolean for if checked or not
            norm = normalise.isChecked()
            conditiontrain = trainbycondition.isChecked()
            # dropdown behaviour goes here <--

            # print statements for testing purposes
            print(superx, supery, superz, svcategories, megax, megay, megaz,
                  mvcategories, voxelnum, trainingnum)
            if bg:
                print("bg")
            if norm:
                print("norm")
            if conditiontrain:
                print("conditiontrain")

            self.close()

        done.clicked.connect(donePressed)
        winlayout.addWidget(superbox, 0, 0, 1, 1)
        winlayout.addWidget(megabox, 0, 1, 1, 1)
        winlayout.addWidget(mainbox, 1, 0, 1, 2)
        winlayout.addWidget(reset, 2, 0, 1, 1)
        winlayout.addWidget(done, 2, 1, 1, 1)
        winlayout.setAlignment(Qt.AlignLeft)
        self.setLayout(winlayout)

class segmentationWindow(QDialog):
    def __init__(self):
        super(segmentationWindow, self).__init__()
        self.setWindowTitle("Organoid Segmentation")
        self.setLayout(QGridLayout())

        # buttons
        selectmetadata = QPushButton("Select Metadata File")
        segmentationsettings = QPushButton("Segmentation Settings")
        outputpath = QPushButton("Preview/edit output path")
        segment = QPushButton("Segment")
        nextimage = QPushButton("Next Image")
        previmage = QPushButton("Previous Image")

        # button functions
        def setSegmentationSettings():
            newdialog = QDialog()
            newdialog.setWindowTitle("Set Segmentation Settings")
            newdialog.setLayout(QGridLayout())
            minarea = QLineEdit()
            intensity = QLineEdit()
            radius = QLineEdit()
            smoothing = QLineEdit()
            scale = QLineEdit()
            entropy = QLineEdit()
            maximage = QLineEdit()
            confirm = QPushButton("Confirm")
            cancel = QPushButton("Cancel")

            def confirmClicked():
                # do stuff with the values in the line edits
                newdialog.close()
            def cancelClicked():
                newdialog.close()

            confirm.clicked.connect(confirmClicked)
            cancel.clicked.connect(cancelClicked)

            newdialog.layout().addWidget(QLabel("Min Area Spheroid"), 0, 0, 1, 1)
            newdialog.layout().addWidget(minarea, 0, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Intensity Threshold"), 1, 0, 1, 1)
            newdialog.layout().addWidget(intensity, 1, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Radius Spheroid"), 2, 0, 1, 1)
            newdialog.layout().addWidget(radius, 2, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Smoothing Parameter"), 3, 0, 1, 1)
            newdialog.layout().addWidget(smoothing, 3, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Scale Spheroid"), 4, 0, 1, 1)
            newdialog.layout().addWidget(scale, 4, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Entropy Threshold"), 5, 0, 1, 1)
            newdialog.layout().addWidget(entropy, 5, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Max Image Fraction"), 6, 0, 1, 1)
            newdialog.layout().addWidget(maximage, 6, 1, 1, 1)
            newdialog.layout().addWidget(confirm, 7, 0, 1, 1)
            newdialog.layout().addWidget(cancel, 7, 1, 1, 1)
            newdialog.setFixedSize(newdialog.minimumSizeHint())
            newdialog.show()
            newdialog.exec()


        segmentationsettings.clicked.connect(setSegmentationSettings)

        # image boxes
        focusimage = QGroupBox("Focus Image")
        segmentmap = QGroupBox("Segmentation Map")
        # put images here

        # add everything to layout
        self.layout().addWidget(selectmetadata, 0, 0)
        self.layout().addWidget(segmentationsettings, 1, 0)
        self.layout().addWidget(outputpath, 2, 0)
        self.layout().addWidget(segment, 3, 0)
        self.layout().addWidget(focusimage, 0, 1, 3, 1)
        self.layout().addWidget(segmentmap, 0, 2, 3, 1)
        self.layout().addWidget(previmage, 3, 1)
        self.layout().addWidget(nextimage, 3, 2)

class colorchannelWindow(object):
    def __init__(self, ch, color):
        win = QDialog()
        win.setWindowTitle("Color Channel Picker")
        title = QLabel("Channels")
        title.setFont(QFont('Arial', 25))
        win.setLayout(QFormLayout())
        win.layout().addWidget(title)
        self.btn=[]
        btn_grp = QButtonGroup()
        btn_grp.setExclusive(True)
        self.color=color

        for i in range(ch):
            self.btn.append(QPushButton('Channel_' + str(i+1)))
            #channel button colour is colour of respective channel
            self.btn[i].setStyleSheet('background-color: rgb' +str(tuple((np.array(self.color[i])*255).astype(int))) +';')
            win.layout().addRow(self.btn[i])
            btn_grp.addButton(self.btn[i], i+1)
        print(btn_grp.buttons())

        btn_grp.buttonPressed.connect(self.colorpicker_window)
        win.show()
        win.exec()

    def colorpicker_window(self, button):
            #Qt custom Colorpicker. Update channel button and current colour to selected colour. Update channel color list.
            wincolor=QColorDialog()
            curcolor=(np.array(self.color[int(button.text()[-1])-1])*255).astype(int)
            wincolor.setCurrentColor(QColor.fromRgb(curcolor[0], curcolor[1], curcolor[2]))
            wincolor.exec_()
            rgb_color = wincolor.selectedColor()
            if rgb_color.isValid():
                self.btn[int(button.text()[-1])-1].setStyleSheet('background-color: rgb' +str(rgb_color.getRgb()[:-1]) +';')
                self.color[int(button.text()[-1])-1] = np.array(rgb_color.getRgb()[:-1])/255


class external_windows():
    def buildExtractWindow(self):
        return extractWindow()

    def buildResultsWindow(self):
        return resultsWindow()

    def buildParamWindow(self):
        return paramWindow()

    def buildSegmentationWindow(self):
        return segmentationWindow()

    def buildColorchannelWindow(self):
        return colorchannelWindow()
