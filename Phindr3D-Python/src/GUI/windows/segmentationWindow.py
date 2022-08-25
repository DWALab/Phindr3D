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
from PyQt5.QtGui import *
from PyQt5.QtCore import *

try:
    from ...Data import *
    from ...Segmentation import *
    from .helperclasses import *
except ImportError:
    from src.Data import *
    from src.Segmentation import *
    from src.GUI.windows.helperclasses import *

Generator = Generator()

class segmentationWindow(QDialog):
    def __init__(self, metadata):
        super(segmentationWindow, self).__init__()
        self.setWindowTitle("Organoid Segmentation")
        self.setLayout(QGridLayout())
        self.metadata = Metadata(Generator)
        self.outdir = None
        self.segmentation = Segmentation()
        self.labelIM = None #numpy array or None
        self.focusIM = None #also numpy array or None

        # buttons
        selectmetadata = QPushButton("Select Metadata File")
        segmentationsettings = QPushButton("Segmentation Settings")
        outputpath = QPushButton("Set output path")
        segment = QPushButton("Segment")
        nextimage = QPushButton("Next Image")
        previmage = QPushButton("Prev Image")

        # labels
        selectlabel = QLabel('Metadata File')
        outlabel = QLabel('Ouput Directory')
    
        # image boxes
        focusbox = QGroupBox("Focus Image")
        focuslayout = QVBoxLayout()
        focusplot = MplCanvas(self, width=2, height=2, dpi=100, projection='2d')
        focusplot.setNearFull()
        focuslayout.addWidget(focusplot)
        focusbox.setLayout(focuslayout)
        segmentbox = QGroupBox("Segmentation Map")
        segmentlayout = QVBoxLayout()
        segmentplot = MplCanvas(self, width=2, height=2, dpi=100, projection='2d')
        segmentplot.setNearFull()
        segmentlayout.addWidget(segmentplot)
        segmentbox.setLayout(segmentlayout)

        # button functions
        def setSegmentationSettings(self):
            newdialog = QDialog()
            newdialog.setWindowTitle("Set Segmentation Settings")
            newdialog.setLayout(QGridLayout())
            minarea = QLineEdit(str(self.segmentation.settings['min_area_spheroid']))
            intensity = QLineEdit(str(self.segmentation.settings['intensity_threshold']))
            radius = QLineEdit(str(self.segmentation.settings['radius_spheroid']))
            smoothing = QLineEdit(str(self.segmentation.settings['smoothin_param']))
            scale = QLineEdit(str(self.segmentation.settings['scale_spheroid']))
            entropy = QLineEdit(str(self.segmentation.settings['entropy_threshold']))
            maximage = QLineEdit(str(self.segmentation.settings['max_img_fraction']))
            removeborderbox = QCheckBox()
            removeborderbox.setChecked(self.segmentation.settings['remove_border_objects'])
            confirm = QPushButton("Confirm")
            cancel = QPushButton("Cancel")
            load = QPushButton('Load settings file')
            save2json = QPushButton('Save settings to file')

            def updateSettingDisplay(self):
                minarea.setText(str(self.segmentation.settings['min_area_spheroid']))
                intensity.setText(str(self.segmentation.settings['intensity_threshold']))
                radius.setText(str(self.segmentation.settings['radius_spheroid']))
                smoothing.setText(str(self.segmentation.settings['smoothin_param']))
                scale.setText(str(self.segmentation.settings['scale_spheroid']))
                entropy.setText(str(self.segmentation.settings['entropy_threshold']))
                maximage.setText(str(self.segmentation.settings['max_img_fraction']))
                removeborderbox.setChecked(self.segmentation.settings['remove_border_objects'])
            def updateSettingVals(self):
                try:
                    self.segmentation.settings['min_area_spheroid'] = float(minarea.text())
                    self.segmentation.settings['intensity_threshold'] = float(intensity.text())
                    self.segmentation.settings['radius_spheroid'] = float(radius.text())
                    self.segmentation.settings['smoothin_param'] = float(smoothing.text())
                    self.segmentation.settings['scale_spheroid'] = float(scale.text())
                    self.segmentation.settings['entropy_threshold'] = float(entropy.text())
                    self.segmentation.settings['max_img_fraction'] = float(maximage.text())
                    self.segmentation.settings['remove_border_objects'] = removeborderbox.isChecked()
                    return True
                except ValueError:
                    alert = self.buildErrorWindow('Segmentation settings can only include numerical values.', QMessageBox.Critical)
                    alert.exec()
                    return False
            def confirmClicked(self):
                if updateSettingVals(self):
                    newdialog.close()
            def cancelClicked():
                newdialog.close()
            def loadClicked(self, loadbutton):
                settingfile, dump = QFileDialog.getOpenFileName(newdialog, 'Open File', '', 'Text files (*.json)')
                if os.path.exists(settingfile):
                    try:
                        self.segmentation.loadSettings(settingfile)
                        loadbutton.setToolTip(settingfile)
                        updateSettingDisplay(self)
                    except:
                        alert = self.buildErrorWindow('Failed to load segmentation settings file.', QMessageBox.Critical)
                        alert.exec()
                else:
                    load_setting_win = self.buildErrorWindow("Select valid Segmentation Settings File (.json)", QMessageBox.Critical)
                    load_setting_win.show()
                    load_setting_win.exec()
            def save2jsonClicked(self, savebutton):
                if updateSettingVals(self):
                    savefile, dump = QFileDialog.getSaveFileName(newdialog, 'Save settings', '', '(*.json)')
                    try:
                        self.segmentation.saveSettings(savefile)
                        savebutton.setToolTip(f'Last save at: {savefile}')
                    except FileNotFoundError:
                        alert = self.buildErrorWindow('Settings not saved.', QMessageBox.Critical)
                        alert.exec()
                
            confirm.clicked.connect(lambda: confirmClicked(self))
            cancel.clicked.connect(lambda: cancelClicked())
            load.clicked.connect(lambda: loadClicked(self, load))
            save2json.clicked.connect(lambda: save2jsonClicked(self, save2json))

            newdialog.layout().addWidget(load, 0, 0, 1, 1)
            newdialog.layout().addWidget(save2json, 0, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Min Area Spheroid"), 1, 0, 1, 1)
            newdialog.layout().addWidget(minarea, 1, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Intensity Threshold"), 2, 0, 1, 1)
            newdialog.layout().addWidget(intensity, 2, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Radius Spheroid"), 3, 0, 1, 1)
            newdialog.layout().addWidget(radius, 3, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Smoothing Parameter"), 4, 0, 1, 1)
            newdialog.layout().addWidget(smoothing, 4, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Scale Spheroid"), 5, 0, 1, 1)
            newdialog.layout().addWidget(scale, 5, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Entropy Threshold"), 6, 0, 1, 1)
            newdialog.layout().addWidget(entropy, 6, 1, 1, 1)
            newdialog.layout().addWidget(QLabel("Max Image Fraction"), 7, 0, 1, 1)
            newdialog.layout().addWidget(maximage, 7, 1, 1, 1)
            newdialog.layout().addWidget(QLabel('Remove Border Objects'), 8, 0, 1, 1)
            newdialog.layout().addWidget(removeborderbox, 8, 1, 1, 1)
            newdialog.layout().addWidget(confirm, 9, 0, 1, 1)
            newdialog.layout().addWidget(cancel, 9, 1, 1, 1)
            newdialog.setFixedSize(newdialog.minimumSizeHint())
            newdialog.show()
            newdialog.exec()
        # End setSegmentationSettings
        
        def loadMetadata(self, loadbutton):
            filename, dump = QFileDialog.getOpenFileName(self, 'Select Metadata File', '', 'Text files (*.txt)')
            if os.path.exists(filename):
                try:
                    self.metadata.loadMetadataFile(filename)
                    loadbutton.setToolTip(filename)
                    if len(filename) > 25:
                        loadbutton.setText(f'{filename[:10]}...{filename[-10:]}')
                    else:
                        loadbutton.setText(filename)

                except MissingChannelStackError:
                    errortext = "Metadata Extraction Failed: Channel/Stack/ImageID column(s) missing and/or invalid."
                    alert = self.buildErrorWindow(errortext, QMessageBox.Critical)
                    alert.exec()
                except FileNotFoundError:
                    alert = self.buildErrorWindow("Metadata Extraction Failed: Metadata file does not exist.")
                    alert.exec()
            else:
                load_metadata_win = self.buildErrorWindow("Select Valid Metadata File (.txt)", QMessageBox.Critical)
                load_metadata_win.show()
                load_metadata_win.exec()
        # End loadMetadata

        def setOutputPath(self, outputbutton):
            dirname = QFileDialog.getExistingDirectory(self, 'Select Segmentation Output Directory')
            if os.path.exists(dirname):
                self.outdir = dirname
                if len(dirname) > 25:
                    outputbutton.setText(f'{dirname[:10]}...{dirname[-10:]}')
                else:
                    outputbutton.setText(dirname)
                self.segmentation.outputDir = dirname
                outputbutton.setToolTip(dirname)
            else:
                alert = self.buildErrorWindow("Select Valid Directory.", QMessageBox.Critical)
                alert.exec()
        # End setOutputPath
        
        def showSegmentation(self):
            if self.focusIM is None or self.labelIM is None:
                pass
            else:
                #stuff from helperclasses here since I want to display the images.
                segmentplot.axes.clear()
                segmentplot.axes.imshow(self.labelIM, 'tab10')
                segmentplot.axes.set_axis_off()
                segmentplot.draw()
                focusplot.axes.clear()
                focusplot.axes.imshow(self.focusIM, 'gray')
                focusplot.axes.set_axis_off()
                focusplot.draw()
        # End showSegmentation

        def nextimageClicked(self):
            self.focusIM, self.labelIM = self.segmentation.getNextIMs()
            showSegmentation(self)
        # End nextimageClicked

        def previmageClicked(self):
            self.focusIM, self.labelIM = self.segmentation.getPrevIMs()
            showSegmentation(self)
        # End previmageClicked
        
        def segmentImages(self):
            if not self.metadata.metadataLoadSuccess:
                loadMetadata(self, selectmetadata)
                if not self.metadata.metadataLoadSuccess:
                    return None
            if self.segmentation.outputDir == None:
                setOutputPath(self, outputpath)
                if self.segmentation.outputDir == None:
                    return None
            alert = self.buildErrorWindow('Start Segmentation?', QMessageBox.Information)
            alert.exec()
            self.segmentation.createSubfolders()
            self.segmentation.RunSegmentation(self.metadata)
            if self.segmentation.segmentationSuccess:
                alert = self.buildErrorWindow('Segmentation Completed.', QMessageBox.Information)
                alert.exec()
                self.focusIM, self.labelIM = self.segmentation.getCurrentIMs()
                showSegmentation(self)   
            else:
                alert = self.buildErrorWindow('Segmentation Failed.', QMessageBox.Critical)
                alert.exec()
        # End segment Images   

        selectmetadata.clicked.connect(lambda: loadMetadata(self, selectmetadata))
        outputpath.clicked.connect(lambda: setOutputPath(self, outputpath))
        segmentationsettings.clicked.connect(lambda: setSegmentationSettings(self))
        segment.clicked.connect(lambda: segmentImages(self))
        nextimage.clicked.connect(lambda: nextimageClicked(self))
        previmage.clicked.connect(lambda: previmageClicked(self))

        # add everything to layout
        self.layout().addWidget(selectlabel, 0, 0)
        self.layout().addWidget(selectmetadata, 1, 0)
        self.layout().addWidget(outlabel, 2, 0)
        self.layout().addWidget(outputpath, 3, 0)
        self.layout().addWidget(segmentationsettings, 4, 0)
        self.layout().addWidget(segment, 5, 0)
        self.layout().addWidget(focusbox, 0, 1, 5, 5)
        self.layout().addWidget(segmentbox, 0, 6, 5, 5)
        self.layout().addWidget(previmage, 5, 3, 1, 1)
        self.layout().addWidget(nextimage, 5, 8, 1, 1)


    def buildErrorWindow(self, errormessage, icon, errortitle="ErrorDialog"):
        alert = QMessageBox()
        alert.setWindowTitle(errortitle)
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

# End segmentationWindow class