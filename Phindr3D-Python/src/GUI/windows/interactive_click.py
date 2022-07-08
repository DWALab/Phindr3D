from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import proj3d
import matplotlib
import numpy as np
import pandas as pd
import time
from more_itertools import locate
from PIL import Image
from ..analysis_scripts import *
from .helperclasses import MplCanvas

#Callback will open image associated with data point. Note: in 3D plot pan is hold left-click swipe, zoom is hold right-click swipe
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

#Callback will open image associated with data point. Note: in 3D plot pan is hold left-click swipe, zoom is hold right-click swipe
class interactive_points():
    def __init__(self, main_plot, projection, data, labels, feature_file, color, imageID):
        self.main_plot=main_plot
        self.projection=projection
        self.data=data
        self.labels=labels
        self.feature_file=feature_file
        self.color=color
        self.imageID=imageID

    def buildImageViewer(self, x_data, label, cur_label, index, color, feature_file, imageID):

                win = QDialog()
                win.resize(1000, 1000)
                win.setWindowTitle("ImageViewer")
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
                main_plot = MplCanvas(self, width=12, height=12, dpi=100, projection='2d')
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
                grid.addWidget(pjt_box, 1, 1, Qt.AlignCenter)
                grid.addWidget(adjustbar, 0, 2)

                win.setLayout(grid)

                self.channel_display(adjustbar, main_plot, color, x_data, label, cur_label, index, feature_file, file_info, ch_info, imageID)
                adjustbar.valueChanged.connect(lambda: self.channel_display(adjustbar, main_plot, color, x_data, label, cur_label, index, feature_file, file_info, ch_info, imageID))
                win.show()
                win.exec()

    def channel_display(self, slicescrollbar, img_plot, color, x, label, cur_label, index, feature_file, file_info, ch_info, imageID):
            if feature_file:
                # extract image details from feature file
                data = pd.read_csv(feature_file[0], sep="\t", na_values='NaN')
                ch_len = (list(np.char.find(list(data.columns), 'Channel_')).count(0))
                data = pd.read_csv(data["MetadataFile"].str.replace(r'\\', '/', regex=True).iloc[0], sep="\t",  na_values='NaN')

                #update info labels
                ch_names = ['<font color= "#' + str('%02x%02x%02x' % (int(color[i-1][0]*255), int(color[i-1][1]*255), int(color[i-1][2]*255))) + '">' + "Channel_" + str(i) + "</font>" for i in
                            range(1, ch_len + 1, 1)]
                ch_names='<br>'.join(ch_names)
                ch_info.setText("Channels<br>"+ch_names)
                meta_loc=0
                stacks=0
                if len(self.labels)>1:
                    cur_ind=list(locate(label, lambda x: x==cur_label))[index]
                    cur_ind=imageID[cur_ind]
                    stacks=data[data["ImageID"] == cur_ind]["Channel_1"]
                    meta_loc=stacks.index[0]
                    stacks=stacks.shape[0]
                else:
                    stacks = data[data["ImageID"] == index+1]["Channel_1"]
                    meta_loc=stacks.index[0]
                    stacks = stacks.shape[0]
                file_info.setText("Filename: " + data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[meta_loc+slicescrollbar.value()])
                slicescrollbar.setMaximum(stacks-1)

                # initialize array as image size with # channels
                rgb_img = Image.open(data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[meta_loc+slicescrollbar.value()]).size
                rgb_img = np.empty((rgb_img[1], rgb_img[0], 3, ch_len))

                # threshold/colour each image channel
                for ind, rgb_color in zip(range(slicescrollbar.value(), slicescrollbar.value() + ch_len),color):
                    ch_num = str(ind - slicescrollbar.value() + 1)
                    data['Channel_' + ch_num] = data['Channel_' + ch_num].str.replace(r'\\', '/', regex=True)
                    cur_img = np.array(Image.open(data['Channel_' + ch_num].iloc[meta_loc+slicescrollbar.value()]))
                    threshold = getImageThreshold(cur_img)
                    cur_img[cur_img <= threshold] = 0
                    cur_img = np.dstack((cur_img, cur_img, cur_img))
                    rgb_img[:, :, :, int(ch_num) - 1] = cur_img * rgb_color

                # compute average and norm to mix colours
                divisor = np.sum(rgb_img != 0, axis=-1)
                tot = np.sum(rgb_img, axis=-1)
                rgb_img = np.divide(tot, divisor, out=np.zeros_like(tot), where=divisor != 0)
                max_rng = [np.max(rgb_img[:, :, i]) if np.max(rgb_img[:, :, i]) > 0 else 1 for i in range(ch_len)]
                rgb_img = np.divide(rgb_img, max_rng)

                # plot combined channels
                img_plot.axes.clear()
                img_plot.axes.imshow(rgb_img)
                img_plot.draw()

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
            self.buildImageViewer(self.data[0],self.labels,label, imin,self.color,self.feature_file, self.imageID)
