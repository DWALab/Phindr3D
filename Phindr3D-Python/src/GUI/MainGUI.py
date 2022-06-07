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
from .external_windows import *
import pyqtgraph as pg
import sys

class load_file(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("load file")
        self.resize(500, 200)

        test_label = QLabel("Filler.......")
        layout = QFormLayout()
        layout.addRow(test_label)
        self.setLayout(layout)

        #open window on center of screen
        frame = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(cp)
        self.move(frame.topLeft())

class MainGUI(QWidget, external_windows):
    """Defines the main GUI window of Phindr3D"""

    def __init__(self):
        """MainGUI constructor"""
        QMainWindow.__init__(self)
        super(MainGUI, self).__init__()
        self.foundMetadata = False

        self.setWindowTitle("Phindr3D")

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
        nextimage = QPushButton("Next Image")
        phind = QPushButton("Phind")
        # Button behaviour defined here
        def metadataError(buttonPressed):
            if not self.foundMetadata:
                alert = self.buildErrorWindow("Metadata not found!!", QMessageBox.Critical)
                alert.exec()
            elif buttonPressed == "Set Voxel Parameters":
                winp = self.buildParamWindow()
                winp.show()
                winp.exec()
            elif buttonPressed == "Set Channel Colors":
                color = QColorDialog.getColor()
                return color

        def exportError():
            if not self.foundMetadata:
                alert = self.buildErrorWindow("No variables to export!!", QMessageBox.Critical)
                alert.exec()

        def loadMetadata():
            filename, dump = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
            if filename != '':
                self.foundMetadata = True
                print(filename)
                # When meta data is loaded, using the loaded data, change the data for image viewing
                # Consider adding another class to store all of the data (GUIDATA in MATLab?)

        # metadataError will check if there is metadata. If there is not, create error message.
        # Otherwise, execute button behaviour, depending on button (pass extra parameter to
        # distinguish which button was pressed into metadataError()?)
        setvoxel.clicked.connect(lambda: metadataError("Set Voxel Parameters"))
        loadmeta.clicked.connect(lambda: loadMetadata())
        sv.clicked.connect(lambda: metadataError("SV"))
        mv.clicked.connect(lambda: metadataError("MV"))
        adjustbar.valueChanged.connect(lambda: metadataError("Adjust Image Threshold"))
        setcolors.clicked.connect(lambda: metadataError("Set Channel Colors"))
        slicescrollbar.valueChanged.connect(lambda: metadataError("Slice Scroll"))
        nextimage.clicked.connect(lambda: metadataError("Next Image"))
        phind.clicked.connect(lambda: metadataError("Phind"))
        # QScrollBar.valueChanged signal weird, one tap would cause the signal to repeat itself
        # multiple times, until slider reached one end. Thus, changed QScrollBar to QSlider.

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
            self.foundMetadata = not self.foundMetadata

        createmetadata.triggered.connect(extractMetadata)
        loadmetadata.triggered.connect(loadMetadata)
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
        vertical = QVBoxLayout()
        vertical.addWidget(setcolors)
        vertical.addWidget(slicescroll)
        vertical.addWidget(slicescrollbar)
        vertical.addWidget(nextimage)
        imageparam.setLayout(vertical)
        layout.addWidget(imageparam, 2, 0)

        imageparam.setFixedSize(imageparam.minimumSizeHint())
        analysisparam.setFixedSize(analysisparam.minimumSizeHint())
        analysisparam.setFixedWidth(imageparam.minimumWidth())

        # Phind button
        layout.addWidget(phind, 3, 0, Qt.AlignCenter)

        # Box for image (?)
        imgwindow = QGroupBox()
        imgwindow.setFlat(True)
        img = QLabel()
        # Set image to whatever needs to be displayed (temporarily set as icon for testing purposes)
        pixmap = QPixmap('C:\Program Files\Git\Phindr3D\phindr3d_icon.png')
        imgdimension = imageparam.height() + analysisparam.height()
        pixmap = pixmap.scaled(imgdimension, imgdimension)
        img.setPixmap(pixmap)
        imagelayout = QVBoxLayout()
        imagelayout.addWidget(img)
        imgwindow.setLayout(imagelayout)
        layout.addWidget(imgwindow, 1, 1, 3, 1)
        self.setLayout(layout)

        #mainGUI buttons clicked
        #loadmeta.clicked.connect(self.file_window_show)

    def aboutAlert(self):
        alert = QMessageBox()
        alert.setText("talk about the program")
        alert.setWindowTitle("About")
        alert.exec()

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def file_window_show(self):
        self.load_file_window = load_file()
        self.load_file_window.show()

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