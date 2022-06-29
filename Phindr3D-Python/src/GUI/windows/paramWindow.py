from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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
        normalise = QCheckBox("Normalise Intensity\n Per Condition")
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