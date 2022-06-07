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
import matplotlib
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.spatial import distance
import numpy as np
from PIL import Image
import sys

#Matplotlib Figure and Interactive Mouse-Click Callback Classes
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=5, dpi=100, projection="3d"):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if projection == "3d":
            self.axes = self.fig.add_subplot(111, projection=projection)
        else:
            self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class interactive_points(object):
    def __init__(self, xdata, ydata, sc, main_plot, projection):
        self.xdata=xdata
        self.ydata=ydata
        self.scbounds=sc
        self.main_plot=main_plot
        self.projection=projection

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

        #for debugging
        '''
        if event.button is MouseButton.LEFT:
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                      ('double' if event.dblclick else 'single', event.button,
                       event.x, event.y, event.xdata, event.ydata))
        '''

        if event.inaxes is not None:
            #find x & y axis tolerance
            xlim=self.scbounds.axes.get_xlim()
            ylim=self.scbounds.axes.get_ylim()
            xtol=0.015*abs(abs(xlim[0])-abs(xlim[1]))+np.exp(-(abs(abs(xlim[0])-abs(xlim[1]))/500))/50
            ytol=0.015*abs(abs(ylim[0])-abs(ylim[1]))+np.exp(-(abs(abs(ylim[0])-abs(ylim[1]))/500))/50

            #when clicked locate closest data point
            pt_closest= distance.cdist([(event.xdata,event.ydata)], list(zip(self.xdata,self.ydata))).argmin()
            xclose=self.xdata[pt_closest]
            yclose=self.ydata[pt_closest]

            #create pop-up figure and plot if clicked data point within tolerance
            plt.figure(1)

            if xclose-xtol < event.xdata < xclose+xtol and yclose-ytol < event.ydata < yclose+ytol:
                winc=self.winc
                winc.show()

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
        imagerootbox.setText(directory)
        imagerootbox.setFixedSize(300, 60)
        imagerootbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        imagerootbox.setFont(largetext)

        selectimage = QPushButton("Select Image Directory")
        selectimage.setFixedSize(selectimage.minimumSizeHint())
        selectimage.setFixedHeight(40)

        samplefilebox = QTextEdit()
        samplefilebox.setReadOnly(True)
        samplefilebox.setText(samplefilename)
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

        cancel.clicked.connect(self.close)

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
        resetview = plotproperties.addAction("Reset Plot View")

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

        # button features go here

        # building layout
        layout = QGridLayout()
        # setup matplotlib figure
        matplotlib.use('Qt5Agg')
        # test points. normally empty list x=[], y=[]
        x = [1, 5]
        y = [7, 2]
        # if !self.foundMetadata:  #x and y coordinates from super/megavoxels
        # x=
        # y=
        projection = "2d"  # Temp Modify to radio
        main_plot = MplCanvas(self, width=5, height=5, dpi=100, projection=projection)
        sc_plot = main_plot.axes.scatter(x, y, [4, 9])

        if not x and not y:
            main_plot.axes.set_ylim(bottom=0)
            main_plot.axes.set_xlim(left=0)

        toolbar = NavigationToolbar(main_plot, self)
        layout.addWidget(toolbar, 0, 0, 1, 1)
        layout.addWidget(main_plot, 1, 0, 1, 1)
        layout.addWidget(box, 2, 0, 1, 1)
        img_click = interactive_points(x, y, sc_plot, main_plot, projection)
        # connect mouse-click to figure
        cid = main_plot.fig.canvas.mpl_connect('button_press_event', img_click)
        layout.setMenuBar(menubar)
        self.setLayout(layout)
        minsize = self.minimumSizeHint()
        minsize.setHeight(self.minimumSizeHint().height() + 200)
        minsize.setWidth(self.minimumSizeHint().width() + 100)
        self.setFixedSize(minsize)

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
        title = QLabel("Organoid Segmentation")
        title.setFont(QFont('Arial', 25))
        self.layout().addWidget(title)
        choosemdata = QPushButton("Select Metadata File")

        # Define function for button behaviour (choose metadata file, select channels, choose output
        # directory, select segmentation channel, loading windows, create directories, TBA)
        def segment():
            filename, dump = QFileDialog.getOpenFileName(self, 'Select Metadata File', '', 'Text file (*.txt)')
            if filename != '':
                win = QDialog()
                selectall = QPushButton("Select All")
                ok = QPushButton("OK")
                cancel = QPushButton("Cancel")
                items = ["Channel 1", "Channel 2", "Channel 3", "Well", "Field", "Stack", "Metadata File", "ImageID"]
                list = QListWidget()
                for item in items:
                    list.addItem(item)
                list.setSelectionMode(QAbstractItemView.MultiSelection)

                selectall.clicked.connect(lambda: list.selectAll())
                cancel.clicked.connect(lambda: win.close())

                # OK button behaviour: User has made their selection, and thus moves on to next step
                def okClicked():
                    win.close()
                    selected = list.selectedItems()
                    if selected == []:
                        print("nothing selected")
                    else:
                        outputdirectory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
                        if outputdirectory != '':
                            newlist = QListWidget()
                            for item in items:
                                newlist.addItem(item)
                            newlist.setSelectionMode(QAbstractItemView.SingleSelection)
                            wina = QDialog()
                            wina.setLayout(QGridLayout())
                            wina.layout().addWidget(newlist, 0, 0, 2, 2)
                            secondok = QPushButton("OK")
                            secondcancel = QPushButton("Cancel")
                            secondcancel.clicked.connect(lambda: wina.close())
                            progress = QProgressBar()
                            # Again, new OK button behaviour: write images, with progress bar to track status
                            def secondOkClicked():
                                wina.close()
                                selecteditem = newlist.selectedItems()
                                if selecteditem == []:
                                    print("nothing selected")
                                else:
                                    completed = 0
                                    winb = QDialog()
                                    winb.setLayout(QGridLayout())
                                    progress.setFixedSize(500, 20)
                                    dl = QPushButton("Download")
                                    winb.layout().addWidget(progress, 0, 0, 2, 2)
                                    winb.layout().addWidget(dl, 2, 1, 1, 1)
                                    winb.show()
                                    while completed < 100:
                                        completed += 0.0001
                                        progress.setValue(int(completed))
                                    winb.exec()

                            secondok.clicked.connect(lambda: secondOkClicked())
                            wina.layout().addWidget(secondok, 2, 0, 1, 1)
                            wina.layout().addWidget(secondcancel, 2, 1, 1, 1)
                            wina.show()
                            wina.exec()

                ok.clicked.connect(lambda: okClicked())

                win.setLayout(QGridLayout())
                win.layout().addWidget(list, 0, 0, 2, 2)
                win.layout().addWidget(selectall, 2, 0, 1, 2)
                win.layout().addWidget(ok, 3, 0, 1, 1)
                win.layout().addWidget(cancel, 3, 1, 1, 1)
                win.show()
                win.exec()

        choosemdata.clicked.connect(segment)
        self.layout().addWidget(choosemdata)

class external_windows():
    def buildExtractWindow(self):
        return extractWindow()

    def buildResultsWindow(self):
        return resultsWindow()

    def buildParamWindow(self):
        return paramWindow()

    def buildSegmentationWindow(self):
        return segmentationWindow()

