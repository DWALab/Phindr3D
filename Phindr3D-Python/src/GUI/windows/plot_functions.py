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

import numpy as np
from cv2 import medianBlur
import PIL.Image
from .colorchannelWindow import *
import matplotlib
import matplotlib.pyplot as plt
from math import ceil, floor
from textwrap import fill
from .helperclasses import *
import json
try:
    from ...Clustering import *
    from ...Data.DataFunctions import *
    from ...Data.Metadata import *
    from ...PhindConfig.PhindConfig import PhindConfig
except ImportError:
    from src.Clustering import Clustering
    from src.Data.DataFunctions import *

def treatment_bounds(self, data, bounds, id):

    try:
        trt = data['Treatment'].iloc[id]
        trt_loc =int(np.where(data['Treatment'].unique() == trt)[0])
        bound = [bounds[0][trt_loc], bounds[1][trt_loc]]
        return(bound)
    except:
        win = errorWindow("Error TreatmentNorm","intensityNormPerTreatment was set but no Treatment Column was found in Metadata")
        return(False)


def merge_channels(data, rgb_img, ch_len, scroller_value, color, meta_loc, box, bounds, IntensityThreshold):
    # threshold/colour each image channel
    for ind, rgb_color in zip(range(scroller_value, scroller_value + ch_len), color):
        ch_num = str(ind - scroller_value + 1)
        data['Channel_' + ch_num] = data['Channel_' + ch_num].str.replace(r'\\', '/', regex=True)
        cur_img = np.array(PIL.Image.open(data['Channel_' + ch_num].iloc[meta_loc + scroller_value]))
        # medianfilter for slice or MIP projection
        if box == False:
            cur_img = medianBlur(cur_img, 3)
        cur_img= (cur_img - bounds[0][int(ch_num)-1])/(bounds[1][int(ch_num)-1]-bounds[0][int(ch_num)-1]) #bounds from metadata functions compute
        cur_img[cur_img < IntensityThreshold[0][int(ch_num)-1]] = 0
        cur_img[cur_img > 1] = 1
        cur_img = np.dstack((cur_img, cur_img, cur_img))
        rgb_img[int(ch_num) - 1, :, :, :] = np.multiply(cur_img, rgb_color)
    # compute average and norm to mix colours
    rgb_img = np.sum(rgb_img, axis=0)
    max_rng = [np.max(rgb_img[:, :, i]) if np.max(rgb_img[:, :, i]) > 0 else 1 for i in range(3)]
    rgb_img = np.divide(rgb_img, max_rng)
    return (rgb_img)

def result_plot(self, X, projection, plot, new_plot):
    #reset plot
    self.main_plot.axes.clear()
    del self.plots[:]
    if new_plot:
        dim=int(projection[0])
        #send to clustering.py for PCA, Sammon, t-SNE analysis
        P=Clustering.Clustering().plot_type(X, dim, plot)
        self.plot_data.clear()
        #save new x, y, z data
        self.plot_data.append(P[:,0])
        self.plot_data.append(P[:,1])
        if dim==3:
            self.plot_data.append(P[:, 2])
        else:
            self.plot_data.append(np.zeros(len(self.plot_data[-1])))
    #plot data
    colors= plt.cm.get_cmap('gist_ncar')(range(0, 255, floor(255/len(np.unique(self.labels)))))
    if len(np.unique(self.labels))>1:
        for label, i in zip(np.unique(self.labels), range(len(np.unique(self.labels)))):
            self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0][np.where(np.array(self.labels)==label)[0]], self.plot_data[1][np.where(np.array(self.labels)==label)[0]], self.plot_data[2][np.where(np.array(self.labels)==label)[0]], label=label,
                            s=10, alpha=1, color=[colors[i]], depthshade=False, picker=1.5, cmap=colors))
    else:
        self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], label=self.labels[0],
                        s=10, alpha=1, color=[colors[0]], depthshade=False, picker=2, cmap=colors))
    legend_format(self, plot, colors, new_plot)

def legend_format(self, plot, colors, new_plot):
    #default legend formating
    cols=2
    bbox=(1.3, 0.75)
    text=""
    handle=[matplotlib.patches.Patch(color=colour, label=label) for label, colour in zip(self.labels, colors)]
    #increase legend columns if too many labels
    if len(self.labels)>1:
        text=max(self.labels, key = len)
    if len(np.unique(self.labels))>40:
        cols=cols + ceil(len(np.unique(self.labels))/40)
        bbox=(1.6, 0.5)
    #textwrap if longer than 10 characters
    if len(text)>10:
        labels = [fill(lbl, 20) for lbl in np.unique(self.labels)]
        self.main_plot.axes.legend(handle, labels, bbox_to_anchor=bbox, ncol=cols,loc='center right')
    else:
        self.main_plot.axes.legend(handle, np.unique(self.labels),bbox_to_anchor=bbox, ncol=cols, loc='center right')
    #axis/title labels
    self.main_plot.axes.set_title(plot + " Plot")
    self.main_plot.axes.set_xlabel(plot + " 1")
    self.main_plot.axes.set_ylabel(plot + " 2")
    #save original x,y,z axis limits for resetview
    if new_plot:
        self.original_xlim=[self.plots[-1].axes.get_xlim3d()[0], self.plots[-1].axes.get_xlim3d()[1]]
        self.original_ylim=[self.plots[-1].axes.get_ylim3d()[0], self.plots[-1].axes.get_ylim3d()[1]]
        self.original_zlim=[self.plots[-1].axes.get_zlim3d()[0], self.plots[-1].axes.get_zlim3d()[1]]
    self.main_plot.draw()

def reset_view(self):
    #reset to starting x, y, z limit
    self.main_plot.axes.set_xlim3d(self.original_xlim)
    self.main_plot.axes.set_ylim3d(self.original_ylim)
    self.main_plot.axes.set_zlim3d(self.original_zlim)
    #xy-plane view
    self.main_plot.axes.view_init(azim=-90, elev=90)
    self.main_plot.draw()

def legend_colors(self):
    #get plot rgb values
    map_colors=[np.array(plot.get_facecolor()[0][0:3]) for plot in self.plots]
    #GUI colorpicker
    colors = colorchannelWindow(len(np.unique(self.labels)), map_colors[:], "Custom Colour Picker", "Labels", np.unique(self.labels))
    colors=np.array(colors.color)
    #change plot colours
    if np.array_equal(colors, np.array(map_colors))==False:
        legend = self.main_plot.axes.get_legend()
        if len(np.unique(self.labels))>1:
            for i in range(len(np.unique(self.labels))):
                self.plots[i].set_color(colors[i])
                legend.legendHandles[i].set_color(colors[i])
        else:
            self.plots[0].set_color(colors[0])
            legend.legendHandles[0].set_color(colors[0])
        self.main_plot.draw()

#export current plot data and x, y, z limits
def save_file(self, map):
    name = QFileDialog.getSaveFileName(self, 'Save File')[0]
    if name:
        info = {
                'plot_projection': map,
                'plot_coordinates': [data.tolist() for data in self.plot_data],
                'x_limit': self.original_xlim,
                'y_limit': self.original_ylim,
                'z_limit': self.original_zlim,
        }
        with open(name+'.json', 'w') as f:
            json.dump(info, f)

#import plot data
def import_file(self, map_dropdown, colordropdown, twod, threed):
    filename= QFileDialog.getOpenFileName(self, 'Open Plot Data JSON File', '', 'JSON file (*.json)')[0]
    if filename != '':
        with open(filename, "r") as f:
            try:
                data=json.load(f)
                if list(data.keys())==['plot_projection','plot_coordinates','x_limit','y_limit','z_limit']:
                    self.plot_data.clear()
                    self.plot_data.extend([np.array(plot_data) for plot_data in data.get('plot_coordinates')])
                    self.original_xlim = data.get('x_limit')
                    self.original_ylim = data.get('y_limit')
                    self.original_zlim = data.get('z_limit')
                    map_dropdown.setCurrentIndex(map_dropdown.findText(data.get('plot_projection')))
                reset_view(self)
                #2d/3d set
                if np.all(self.plot_data[2]) != 0:
                    threed.setChecked(True)
                else:
                    twod.setChecked(True)
                self.loadFeaturefile(colordropdown, map_dropdown.currentText(), False)
            except:
                errorWindow("Import Plot Data Error", "Check if correct file. Requires Following Labels: plot_projection, plot_coordinates, x_limit , y_limit ,z_limit")
