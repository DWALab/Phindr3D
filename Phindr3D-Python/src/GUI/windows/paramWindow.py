# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of Phindr3D <https://github.com/DWALab/Phindr3D>.
#
# Phindr3D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Phindr3D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Phindr3D.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class paramWindow(QDialog):
    """Build a GUI window for setting voxel parameters."""
    def __init__(self, metacolumns, supercoords, svcategories, megacoords,
            mvcategories, voxelnum, trainingnum, bg, norm, conditiontrain,
            trainingcol, treatmentcol):
        """Construct the GUI window for setting voxel parameters."""
        super(paramWindow, self).__init__()
        self.setWindowTitle("Set Parameters")
        self.done = False
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
        superxin.setText(str(supercoords[0]))
        superyin.setText(str(supercoords[1]))
        superzin.setText(str(supercoords[2]))
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
        svnum.setText(str(svcategories))
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
        megaxin.setText(str(megacoords[0]))
        megayin.setText(str(megacoords[1]))
        megazin.setText(str(megacoords[2]))
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
        mvnum.setText(str(mvcategories))
        megabox.layout().addWidget(mvnum, 1, 1, 1, 1)
        megabox.layout().addWidget(QLabel("#MV\n Categories"), 1, 0, 1, 1)
        megabox.layout().addWidget(megasizebox, 0, 0, 1, 2)
        megabox.setFixedSize(superbox.size())

        # main box
        mainbox = QGroupBox()
        mainbox.setLayout(QGridLayout())
        voxelcategories = QLineEdit()
        voxelcategories.setFixedWidth(30)
        voxelcategories.setText(str(voxelnum))
        trainingimages = QLineEdit()
        trainingimages.setFixedWidth(30)
        trainingimages.setText(str(trainingnum))
        usebackground = QCheckBox("Use Background Voxels for comparing")
        usebackground.setChecked(bg)
        normalise = QCheckBox("Normalise Intensity\n Per Condition")
        normalise.setChecked(norm)
        trainbycondition = QCheckBox("Train by condition")
        trainbycondition.setChecked(conditiontrain)
        normtreatfilter = QComboBox()
        normtreatfilter.addItems(metacolumns)
        normtreatfilter.setEnabled(False)
        trainfilter = QComboBox()
        trainfilter.addItems(metacolumns)
        trainfilter.setEnabled(False)
        normalise.clicked.connect(
            lambda: normtreatfilter.setEnabled(not normtreatfilter.isEnabled()))
        trainbycondition.clicked.connect(
            lambda: trainfilter.setEnabled(not trainfilter.isEnabled()))

        mainbox.layout().addWidget(QLabel("#Voxel\nCategories"), 0, 0, 1, 1)
        mainbox.layout().addWidget(voxelcategories, 0, 1, 1, 1)
        mainbox.layout().addWidget(QLabel("#Training\nImages"), 0, 3, 1, 1)
        mainbox.layout().addWidget(trainingimages, 0, 4, 1, 1)
        mainbox.layout().addWidget(usebackground, 1, 0, 1, 6)
        mainbox.layout().addWidget(normalise, 2, 0, 1, 3)
        mainbox.layout().addWidget(trainbycondition, 2, 3, 1, 3)
        mainbox.layout().addWidget(normtreatfilter, 3, 0, 1, 3)
        mainbox.layout().addWidget(trainfilter, 3, 3, 1, 3)
        mainbox.setFixedWidth(mainbox.minimumSizeHint().width() + 50)
        mainbox.setFixedHeight(mainbox.minimumSizeHint().height() + 20)

        # reset and done buttons
        reset = QPushButton("Reset")
        done = QPushButton("Done")

        if treatmentcol!='':
            normtreatfilter.setEnabled(True)
            normtreatfilter.setCurrentIndex(normtreatfilter.findText(treatmentcol))
        if trainingcol!='':
            trainfilter.setEnabled(True)
            trainfilter.setCurrentIndex(trainfilter.findText(trainingcol))

        # button behaviours
        def donePressed():
            """Respond to the user clicking Done on the parameter window.

            When done is pressed, all the inputted values are returned,
            stored in their place and the window closes.
            """
            try:
                self.superx = int(superxin.text())
                self.supery = int(superyin.text())
                self.superz = int(superzin.text())
                self.svcategories = int(svnum.text())
                self.megax = int(megaxin.text())
                self.megay = int(megayin.text())
                self.megaz = int(megazin.text())
                self.mvcategories = int(mvnum.text())
                self.voxelnum = int(voxelcategories.text())
                self.trainingnum = int(trainingimages.text())
                self.bg = usebackground.isChecked() # For checkboxes, return boolean for if checked or not
                self.norm = normalise.isChecked()
                self.conditiontrain = trainbycondition.isChecked()
                self.done = True
                if trainbycondition.isChecked():
                    self.trainingcol=trainfilter.currentText()
                else:
                    self.trainingcol=''
                if normalise.isChecked():
                    self.normintensitycol=normtreatfilter.currentText()
                else:
                    self.normintensitycol=''
                # dropdown behaviour goes here <--
                self.close()
            except ValueError:
                alert = QMessageBox()
                alert.setWindowTitle("Error")
                alert.setText("Invalid input")
                alert.exec()

        def resetPressed():
            """Reset the parameters to the initial values when window opened."""
            superxin.setText(str(supercoords[0]))
            superyin.setText(str(supercoords[1]))
            superzin.setText(str(supercoords[2]))
            svnum.setText(str(svcategories))
            megaxin.setText(str(megacoords[0]))
            megayin.setText(str(megacoords[1]))
            megazin.setText(str(megacoords[2]))
            mvnum.setText(str(mvcategories))
            voxelcategories.setText(str(voxelnum))
            trainingimages.setText(str(trainingnum))
            usebackground.setChecked(bg)
            normalise.setChecked(norm)
            normtreatfilter.setEnabled(norm)
            if normtreatfilter.findText(treatmentcol)>-1:
                normtreatfilter.setCurrentIndex(normtreatfilter.findText(treatmentcol))
            else:
                normtreatfilter.setCurrentIndex(0)
            trainbycondition.setChecked(conditiontrain)
            trainfilter.setEnabled(conditiontrain)
            if trainfilter.findText(trainingcol)>-1:
                trainfilter.setCurrentIndex(trainfilter.findText(trainingcol))
            else:
                trainfilter.setCurrentIndex(0)
        # resetPressed

        done.clicked.connect(donePressed)
        reset.clicked.connect(resetPressed)
        winlayout.addWidget(superbox, 0, 0, 1, 1)
        winlayout.addWidget(megabox, 0, 1, 1, 1)
        winlayout.addWidget(mainbox, 1, 0, 1, 2)
        winlayout.addWidget(reset, 2, 0, 1, 1)
        winlayout.addWidget(done, 2, 1, 1, 1)
        winlayout.setAlignment(Qt.AlignLeft)
        self.setLayout(winlayout)
    # end constructor