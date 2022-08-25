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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import proj3d
import matplotlib
matplotlib.use('Qt5Agg')
import numpy as np
import pandas as pd
import time
from more_itertools import locate
from .plot_functions import *
from .colorchannelWindow import *
import PIL.Image
import json

Generator = Generator()
#Callback will open image associated with data point. Note: in 3D plot pan is hold left-click swipe, zoom is hold right-click swipe (zoom disabled)
class interactive_points():
    def __init__(self, main_plot, projection, data, labels, feature_file, color, imageID):
        self.main_plot=main_plot
        self.projection=projection
        self.data=data
        self.labels=labels
        self.feature_file=feature_file
        self.color=color[:]
        self.imageID=imageID
    def buildImageViewer(self, label, cur_label, index, color, feature_file, imageID):

                self.win = QDialog()
                self.win.resize(1200, 1000)
                self.win.setWindowTitle("ImageViewer")
                grid = QGridLayout()

                #info layout
                info_box = QVBoxLayout()
                file_info=QLabel("FileName:")
                file_info.setAlignment(Qt.AlignTop)
                file_info.setStyleSheet("background-color: white")
                file_info.setWordWrap(True)
                ch_info=QLabel("Channels\n")
                ch_info.setAlignment(Qt.AlignTop)
                ch_info.setStyleSheet("background-color: white")
                file_info.setFixedWidth(200)
                file_info.setMinimumHeight(350)
                ch_info.setFixedWidth(200)
                ch_info.setMinimumHeight(350)
                info_box.addStretch()
                info_box.addWidget(file_info)
                info_box.addWidget(ch_info)
                info_box.addStretch()
                ch_colour=QPushButton("Set Channel Colours")
                #projection layout
                pjt_box = QGroupBox("Projection Type")
                pjt_type= QHBoxLayout()
                slice_btn = QRadioButton("Slice")
                slice_btn.setChecked(True)
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
                x = []
                y = []
                main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection='2d')
                main_plot.fig.set_facecolor('#f0f0f0')
                main_plot.axes.scatter(x, y)
                main_plot.axes.get_xaxis().set_visible(False)
                main_plot.axes.get_yaxis().set_visible(False)

                # adjustbar layout
                adjustbar = QSlider(Qt.Vertical)
                adjustbar.setMinimum(0)
                adjustbar.setValue(0)
                adjustbar.setFixedWidth(50)
                adjustbar.setPageStep(1)
                adjustbar.setSingleStep(1)
                adjustbar.setStyleSheet(
                    "QSlider::groove:vertical {background-color: #8DE8F6; border: 1px solid;height: 700px;margin: 0px;}"
                    "QSlider::handle:vertical {background-color: #8C8C8C; border: 1px silver; height: 30px; width: 10px; margin: -5px 0px;}")

                #parent layout
                grid.addLayout(info_box, 0, 0)
                grid.addWidget(main_plot, 0, 1)
                grid.addWidget(ch_colour, 1, 0)
                grid.addWidget(pjt_box, 1, 1, Qt.AlignCenter)
                grid.addWidget(adjustbar, 0, 2)
                self.win.setLayout(grid)

                #callbacks
                self.plot_img(adjustbar, main_plot, self.color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt_box)
                adjustbar.valueChanged.connect(lambda: self.plot_img(adjustbar, main_plot, self.color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt_box))
                slice_btn.toggled.connect(lambda: self.plot_img(adjustbar, main_plot, self.color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt_box) if pjt_box.findChildren(QRadioButton)[0].isChecked() else None)
                mit_btn.toggled.connect(lambda: self.plot_img(adjustbar, main_plot, self.color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt_box) if pjt_box.findChildren(QRadioButton)[1].isChecked() else None)
                montage_btn.toggled.connect(lambda: self.plot_img(adjustbar, main_plot, self.color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt_box) if pjt_box.findChildren(QRadioButton)[2].isChecked() else None)
                ch_colour.clicked.connect(lambda: self.color_change((ch_info.text()).count("Channel_"), self.color, "Custom Colour Picker", "Channels", ["Channel_" +str(i+1) for i in range((ch_info.text()).count("Channel_"))], adjustbar, main_plot, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt_box))
                self.win.show()
                self.win.exec()
    def read_featurefile(self, slicescrollbar, color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt):
        if feature_file:
            # extract image details from feature file
            data = pd.read_csv(feature_file[0], sep="\t", na_values='NaN')

            try:
                metadata=Metadata(Generator)
                metadata.loadMetadataFile(data["MetadataFile"].str.replace(r'\\', '/', regex=True).iloc[0])
            except MissingChannelStackError:
                errortext = "Metadata Extraction Failed: Channel/Stack/ImageID column(s) missing and/or invalid."
                errorWindow("Metadata Error", errortext)
            except FileNotFoundError:
                errortext = "Metadata Extraction Failed: Metadata file does not exist."
                errorWindow("Metadata Error", errortext)
            except Exception:
                errortext = "Metadata Extraction Failed: Invalid Image type (must be grayscale)."
                errorWindow("Metadata Error", errortext)

            #getting metadatafile
            data = pd.read_csv(data["MetadataFile"].str.replace(r'\\', '/', regex=True).iloc[0], sep="\t", na_values='NaN')
            ch_len = (list(np.char.find(list(data.columns), 'Channel_')).count(0))
            # update channel labels
            ch_names = ['<font color= "#' + str('%02x%02x%02x' % (
            int(color[i - 1][0] * 255), int(color[i - 1][1] * 255), int(color[i - 1][2] * 255)))
            + '">' + "Channel_" + str(i) + "</font>" for i in range(1, ch_len + 1, 1)]
            ch_names = '<br>'.join(ch_names)
            ch_info.setText("Channels<br>" + ch_names)
            #update filename label
            stacks = 0
            if len(self.labels) > 1:
                cur_ind = list(locate(label, lambda x: x == cur_label))[index]
                row_ind = imageID[cur_ind]
                stacks = data[data["ImageID"] == row_ind]["Channel_1"]
            else:
                stacks = data[data["ImageID"] == index + 1]["Channel_1"]
            meta_loc = stacks.index[0]
            stacks = stacks.shape[0]
            pjt_label="Slice"
            for radio in pjt.findChildren(QRadioButton):
                if radio.isChecked():
                    pjt_label=radio.text()
                    break
            file_text="Filename: " + data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[meta_loc + slicescrollbar.value()] + '\n\n Projection Type: ' + pjt_label
            if len(file_text)>20:
                #prevent text placed off-screen
                file_text=fill(file_text, 25)
            file_info.setText(file_text)
            # lower/upperbounds, threshold for images
            bounds = json.loads(data['bounds'].iloc[0])
            threshold = json.loads(data['intensity_thresholds'].iloc[0])
            if len(np.shape(bounds))>2:
                bounds = treatment_bounds(self, data, bounds, meta_loc)
                if not bounds:
                    self.win.close()
            #only slice projection can use slider
            if pjt.findChildren(QRadioButton)[0].isChecked():
                slicescrollbar.setMaximum(stacks - 1)
            else:
                slicescrollbar.setMaximum(0)
            # initialize array as image size with rgb and # channels
            empty_img = PIL.Image.open(data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[meta_loc + slicescrollbar.value()]).size
            empty_img = np.zeros((ch_len, empty_img[1], empty_img[0], 3))
            return(data, empty_img, meta_loc, stacks, ch_len, bounds, threshold)
    def plot_img(self, slicescrollbar, img_plot, color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt):
        #reset subplots
        allaxes = img_plot.fig.get_axes()
        for ax in allaxes:
            img_plot.fig.delaxes(ax)
        data, empty_img, metaloc, stacks,ch_len, bounds, threshold=self.read_featurefile(slicescrollbar, color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt)

        #slice projection only calculate for current slice
        if pjt.findChildren(QRadioButton)[0].isChecked():
            stacks=1
        #MIP projection case
        elif pjt.findChildren(QRadioButton)[1].isChecked():
            max_img = np.full((empty_img.shape[1], empty_img.shape[2], 3), np.NINF)

        for x in range(1, stacks+1):
            img=merge_channels(data, empty_img, ch_len, slicescrollbar.value(), color, metaloc+x-1, pjt.findChildren(QRadioButton)[2].isChecked(), bounds, threshold)
            #MIP Projection (max intensity projection - take largest element-wise from image stack)
            if pjt.findChildren(QRadioButton)[1].isChecked():
                max_img=np.maximum(max_img, img)
                if x==stacks:
                    img=max_img
            #plotting
            if pjt.findChildren(QRadioButton)[1].isChecked()==False or x==stacks:
                if pjt.findChildren(QRadioButton)[1].isChecked() == False:
                    axes=img_plot.fig.add_subplot(int(np.ceil(np.sqrt(stacks))),int(np.round_(np.sqrt(stacks), decimals=0)),x)
                else:
                    axes = img_plot.fig.add_subplot(1,1,1)
                axes.imshow(img)
                axes.set_aspect(aspect='auto')
                axes.axis('off')
        img_plot.fig.subplots_adjust(wspace=0.0075, hspace=0.0075)
        img_plot.draw()
    def color_change(self, ch, color, win_title, col_title, labels, slicescrollbar, img_plot, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt):
        colors=colorchannelWindow(ch, color, win_title, col_title, labels)
        self.color=colors.color
        self.plot_img(slicescrollbar, img_plot, self.color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt)

    def __call__ (self, event): #picker is right-click activation
        if event.mouseevent.inaxes is not None and event.mouseevent.button is MouseButton.RIGHT:
            #https://github.com/matplotlib/matplotlib/issues/ 19735   ---- code below from github open issue. wrong event.ind coordinate not fixed in current version matplotlib...
            xx = event.mouseevent.x
            yy = event.mouseevent.y
            label = event.artist.get_label()
            label_ind=np.where(np.array(self.labels)==label)[0]
            # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
            x2, y2, z2 = proj3d.proj_transform(self.data[0][label_ind[0]], self.data[1][label_ind[0]], self.data[2][label_ind[0]], self.main_plot.axes.get_proj())
            x3, y3 = self.main_plot.axes.transData.transform((x2, y2))
            # the distance
            d = np.sqrt((x3 - xx) ** 2 + (y3 - yy) ** 2)

            # find the closest by searching for min distance.
            # from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
            imin = 0
            dmin = 10000000
            for i in range(np.shape(label_ind)[0]):
                # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                x2, y2, z2 = proj3d.proj_transform(self.data[0][label_ind[i]], self.data[1][label_ind[i]], self.data[2][label_ind[i]], self.main_plot.axes.get_proj())
                x3, y3 = self.main_plot.axes.transData.transform((x2, y2))
                # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                d = np.sqrt((x3 - xx) ** 2 + (y3 - yy) ** 2)
                # We find the distance and also the index for the closest datapoint
                if d < dmin:
                    dmin = d
                    imin = i
            self.main_plot.axes.scatter3D(self.data[0][label_ind[imin]],
                                        self.data[1][label_ind[imin]],
                                        self.data[2][label_ind[imin]], s=35, facecolor="none",
                                        edgecolor='gray', alpha=1)
            #for debugging
            #print(self.data[0][label_ind[imin]], self.data[1][label_ind[imin]], self.data[2][label_ind[imin]])
            self.main_plot.draw()
            self.main_plot.figure.canvas.draw_idle()
            self.buildImageViewer(self.labels,label, imin,self.color,self.feature_file, self.imageID)
