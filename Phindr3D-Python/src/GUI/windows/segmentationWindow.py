from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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