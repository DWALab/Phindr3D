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

class MainGUI(QWidget):
    """Defines the main GUI window of Phindr3D"""

    def __init__(self):
        """MainGUI constructor"""
        QMainWindow.__init__(self)
        super(MainGUI, self).__init__()

        self.setWindowTitle("Phindr3D")

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignBottom)

        # All widgets initialized here, to be placed in their proper section of GUI
        loadmeta = QPushButton("Load MetaData")
        setvoxel = QPushButton("Set Voxel Parameters")
        sv = QCheckBox("SV")
        mv = QCheckBox("MV")
        adjust = QLabel("Adjust Image Threshold") # placeholder for now
        setcolors = QPushButton("Set Channel Colors")
        slicescroll = QLabel("Slice Scroller") # placeholder for now
        nextimage = QPushButton("Next Image")
        phind = QPushButton("Phind")
        # Button behaviour defined here
        def metadataError():
            if not self.foundMetadata:
                alert = self.buildErrorWindow("Metadata not found!!", QMessageBox.Critical)
                alert.exec()
        # Currently, only error messages will appear, for set voxel button
        setvoxel.clicked.connect(metadataError)

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

        # Menu actions defined here
        def extractMetadata():
            winz = self.buildExtractWindow()
            winz.show()
            winz.exec()

        createmetadata.triggered.connect(extractMetadata)
        # Creating and formatting menubar
        layout.addWidget(menubar)

        # create analysis parameters box (top left box)
        analysisparam = QGroupBox("Analysis Parameters")
        grid = QGridLayout()
        grid.setVerticalSpacing(20)
        grid.addWidget(loadmeta, 0, 0, 1, 2)
        grid.addWidget(setvoxel, 1, 0, 1, 2)
        grid.addWidget(sv, 2, 0)
        grid.addWidget(mv, 2, 1)
        grid.addWidget(adjust, 3, 0, 1, 2)
        analysisparam.setLayout(grid)
        analysisparam.setFixedSize(140, 180)
        layout.addWidget(analysisparam, 1, 0)

        # create image viewing parameters box (bottom left box)
        imageparam = QGroupBox("Image Viewing Parameters")
        imageparam.setAlignment(1)
        vertical = QVBoxLayout()
        vertical.addWidget(setcolors)
        vertical.addWidget(slicescroll)
        vertical.addWidget(nextimage)
        imageparam.setLayout(vertical)
        imageparam.setFixedSize(140, 180)
        layout.addWidget(imageparam, 2, 0)

        # Phind button
        layout.addWidget(phind, 3, 0, Qt.AlignCenter)

        # Box for image (?)
        imgwindow = QGroupBox()
        imgwindow.setFlat(True)
        img = QLabel()
        # Set image to whatever needs to be displayed (temporarily set as icon for testing purposes)
        pixmap = QPixmap('C:\Program Files\Git\Phindr3D\phindr3d_icon.png')

        pixmap = pixmap.scaled(400, 400)
        img.setPixmap(pixmap)
        imagelayout = QVBoxLayout()
        imagelayout.addWidget(img)
        imgwindow.setLayout(imagelayout)
        imgwindow.setFixedSize(400, 400)
        layout.addWidget(imgwindow, 1, 1, 3, 1)
        self.setLayout(layout)

        #mainGUI buttons clicked
        loadmeta.clicked.connect(self.file_window_show)

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def buildExtractWindow(self):
        largetext = QFont("Arial", 12, 1)
        win = QDialog()
        win.setWindowTitle("Extract Metadata")
        directory = "Image Root Directory"
        samplefilename = "Sample File Name"
        layout = QGridLayout()
        imagerootbox = QTextEdit()
        imagerootbox.setReadOnly(True)
        imagerootbox.setText(directory)
        imagerootbox.setFixedSize(300,60)
        imagerootbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        imagerootbox.setFont(largetext)

        selectimage = QPushButton("Select Image Directory")
        selectimage.setFixedSize(130, 30)

        samplefilebox = QTextEdit()
        samplefilebox.setReadOnly(True)
        samplefilebox.setText(samplefilename)
        samplefilebox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        samplefilebox.setFont(largetext)
        samplefilebox.setFixedSize(450, 40)

        expressionbox = QLineEdit()
        expressionbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        expressionbox.setFont(largetext)
        expressionbox.setFixedSize(450, 30)
        expressionbox.setPlaceholderText("Type Regular Expression Here")

        evaluateexpression = QPushButton("Evaluate Regular Expression")
        evaluateexpression.setFixedSize(160, 30)

        outputfilebox = QLineEdit()
        outputfilebox.setAlignment(Qt.AlignCenter)
        outputfilebox.setFont(largetext)
        outputfilebox.setFixedSize(200, 30)
        outputfilebox.setPlaceholderText("Output Metadata File Name")

        createfile = QPushButton("Create File")
        createfile.setFixedSize(100, 30)

        cancel = QPushButton("Cancel")
        cancel.setFixedSize(100, 30)

        # button functions

        cancel.clicked.connect(win.close)


        layout.addWidget(imagerootbox, 0, 0, 1, 2)
        layout.addWidget(selectimage, 0, 2, 1, 1)
        layout.addWidget(samplefilebox, 1, 0, 1, 3)
        layout.addWidget(expressionbox, 2, 0, 1, 3)
        layout.addWidget(evaluateexpression, 3, 0, 1, 1)
        layout.addWidget(outputfilebox, 4, 0, 1, 1)
        layout.addWidget(createfile, 4, 1, 1, 1)
        layout.addWidget(cancel, 4, 2, 1, 1)
        layout.setSpacing(10)
        win.setLayout(layout)
        win.setFixedSize(500, 300)

        return win

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