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
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
import pandas as pd
try:
    from .interactive_click import interactive_points
    from .plot_functions import *
    from ...Training import *
except ImportError:
    from src.GUI.windows.interactive_click import interactive_points
    from src.GUI.windows.plot_functions import *
    from src.Training import *

class resultsWindow(QDialog):
    def __init__(self, color, metadata):
        super(resultsWindow, self).__init__()
        self.setWindowTitle("Results")
        self.feature_file=[]
        self.imageIDs=[]
        self.plots=[]
        self.filtered_data=0
        self.numcluster=None
        self.metadata=metadata
        self.bounds=0
        self.color=color
        #menu tabs
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
        rotation_enable = plotproperties.addAction("3D Rotation Enable")
        rotation_disable = plotproperties.addAction("3D Rotation Disable")
        resetview = plotproperties.addAction("Reset Plot View")

        # defining widgets
        box = QGroupBox()
        boxlayout = QGridLayout()
        selectfile = QPushButton("Select Feature File")
        prevdata = QPushButton("Import Previous Plot Data + Select Feature File")
        exportdata = QPushButton("Export Current Plot Data")
        cmap=QPushButton("Legend Colours")
        map_type = QComboBox()
        map_type.addItems(["PCA","t-SNE","Sammon"])
        twod = QCheckBox("2D")
        threed = QCheckBox("3D")
        dimensionbox = QGroupBox()
        dimensionboxlayout = QHBoxLayout()
        dimensionboxlayout.addWidget(twod)
        dimensionboxlayout.addWidget(threed)
        dimensionbox.setLayout(dimensionboxlayout)
        colordropdown = QComboBox()
        boxlayout.addWidget(QLabel("File Options"), 0, 0, 1, 1)
        boxlayout.addWidget(selectfile, 1, 0, 1, 1)
        boxlayout.addWidget(exportdata, 2, 0, 1, 1)
        boxlayout.addWidget(prevdata, 3, 0, 1, 1)
        boxlayout.addWidget(QLabel("Plot Type"), 0, 1, 1, 1)
        boxlayout.addWidget(map_type, 1, 1, 1, 1)
        boxlayout.addWidget(dimensionbox, 2, 1, 1, 1)
        boxlayout.addWidget(cmap, 2, 2, 1, 1)
        boxlayout.addWidget(QLabel("Color By"), 0, 2, 1, 1)
        boxlayout.addWidget(colordropdown, 1, 2, 1, 1)
        box.setLayout(boxlayout)
        #menu actions activated
        inputfile.triggered.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText(), True))
        selectclasses.triggered.connect(lambda: TrainingFunctions().selectclasses(np.array(self.filtered_data), np.array(self.labels)) if len(self.plot_data)>0 else None)
        estimate.triggered.connect(lambda: Clustering().cluster_est(self.filtered_data) if len(self.plot_data) > 0 else None)
        setnumber.triggered.connect(lambda: self.setnumcluster(colordropdown.currentText()) if len(self.plot_data) > 0 else None)
        piemaps.triggered.connect(lambda: piechart(self.plot_data, self.filtered_data, self.numcluster, np.array(self.labels), [np.array(plot.get_facecolor()[0][0:3]) for plot in self.plots]) if len(self.plot_data) > 0 else None)
        export.triggered.connect(lambda: export_cluster(self.plot_data, self.filtered_data, self.numcluster, self.feature_file[0]) if len(self.plot_data) >0 else None)
        rotation_enable.triggered.connect(lambda: self.main_plot.axes.mouse_init())
        rotation_disable.triggered.connect(lambda: self.main_plot.axes.disable_mouse_rotation())
        resetview.triggered.connect(lambda: reset_view(self))
        exportdata.clicked.connect(lambda: save_file(self, map_type.currentText()))
        prevdata.clicked.connect(lambda: import_file(self, map_type, colordropdown, twod, threed))
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        self.plot_data = []
        self.labels = []
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter3D([], [], [], s=10, alpha=1, depthshade=False)  # , picker=True)
        self.main_plot.axes.set_position([-0.2, -0.05, 1, 1])
        self.original_xlim = sc_plot.axes.get_xlim3d()
        self.original_ylim = sc_plot.axes.get_ylim3d()
        self.original_zlim = sc_plot.axes.get_zlim3d()
        self.projection = "2d"  # update from radiobutton
        #2d vs 3d settings
        def toggle_2d_3d(checkbox_cur, checkbox_prev, dim, plot):
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            check_projection(dim, plot)
        def check_projection(dim, plot):
            if dim == "2d":
                self.projection = dim
                self.main_plot.axes.mouse_init()
                self.main_plot.axes.view_init(azim=-90, elev=90)
                self.main_plot.axes.get_zaxis().line.set_linewidth(0)
                self.main_plot.axes.tick_params(axis='z', labelsize=0)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()
            elif dim == "3d":
                self.projection = dim
                self.main_plot.axes.get_zaxis().line.set_linewidth(1)
                self.main_plot.axes.tick_params(axis='z', labelsize=10)
                self.main_plot.draw()
                self.main_plot.axes.mouse_init(rotate_btn=1, zoom_btn=[])
            if self.feature_file and colordropdown.count() > 0:
                self.data_filt(colordropdown, self.projection, plot, True)

        # button features and callbacks
        selectfile.clicked.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText(), True))
        cmap.clicked.connect(lambda: legend_colors(self) if len(self.labels)>0 else None)
        twod.toggled.connect(lambda: toggle_2d_3d(twod, threed, "2d", map_type.currentText()))
        threed.toggled.connect(lambda: toggle_2d_3d(threed, twod, "3d", map_type.currentText()))
        twod.setChecked(True)
        picked_pt = interactive_points(self.main_plot, self.projection, self.plot_data, self.labels,self.feature_file, self.color, self.imageIDs)
        self.main_plot.fig.canvas.mpl_connect('pick_event', picked_pt)
        colordropdown.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, self.projection, map_type.currentText(),False) if self.feature_file and colordropdown.count() > 0 else None)
        map_type.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, self.projection, map_type.currentText(),True) if self.feature_file and colordropdown.count() > 0 else None)
        # building layout
        layout = QGridLayout()
        toolbar = NavigationToolbar(self.main_plot, self)
        layout.addWidget(toolbar, 0, 0, 1, 1)
        layout.addWidget(self.main_plot, 1, 0, 1, 1)
        layout.addWidget(box, 2, 0, 1, 1)
        layout.setMenuBar(menubar)
        self.setLayout(layout)
        minsize = self.minimumSizeHint()
        minsize.setHeight(self.minimumSizeHint().height() + 700)
        minsize.setWidth(self.minimumSizeHint().width() + 700)
        self.setFixedSize(minsize)

    def loadFeaturefile(self, grouping, plot, new_plot):
        filename, dump = QFileDialog.getOpenFileName(self, 'Open Feature File', '', 'Text files (*.txt)')
        if filename != '':
            try:
                self.feature_file.clear()
                self.feature_file.append(filename)
                print(self.feature_file)
                grouping, cancel=self.color_groupings(grouping)
                if not cancel:
                    self.data_filt(grouping, self.projection, plot, new_plot)
            except:
                if len(self.plot_data)==0:
                    grouping.clear()
                errorWindow("Feature File Error", "Check Validity of Feature File (.txt)", )


    def color_groupings(self, grouping):
        #read feature file
        feature_data = pd.read_csv(self.feature_file[0], sep='\t', na_values='        NaN')
        grouping.blockSignals(True)
        grps=[]
        #Get Channels
        meta_col=pd.read_csv(feature_data["MetadataFile"].str.replace(r'\\', '/', regex=True).iloc[0], nrows=1,  sep="\t", na_values='NaN').columns.tolist()
        col_lbl=np.array([lbl if lbl.find("Channel_")>-1 else np.nan for lbl in meta_col])
        col_lbl=col_lbl[col_lbl!='nan']
        #Get MV and Texturefeatures labels
        self.filt=[]
        filt_lbl=np.array(["MV"])
        if max(feature_data.columns.str.contains("text_", case=False)):
            filt_lbl=np.concatenate((filt_lbl, ["Texture_Features"]))
        #get labels
        chk_lbl=np.array([lbl if lbl[:2].find("MV")==-1 and lbl!='bounds' and lbl!='intensity_thresholds' and lbl[:5]!='text_' else np.nan for lbl in feature_data.columns])
        chk_lbl=chk_lbl[chk_lbl!='nan']
        #select features window
        win=selectWindow(chk_lbl, col_lbl, "Filter Feature File Groups and Channels", "Grouping", "Channels", grps, filt_lbl, self.filt)
        if not win.x_press:
            #change colorby window
            grouping.clear()
            grouping.addItem("No Grouping")
            for col in grps:
                grouping.addItem(col)
            grouping.blockSignals(False)
        return(grouping, win.x_press)

    def data_filt(self, grouping, projection, plot, new_plot):
        filter_data = grouping.currentText()

        # choose dataset to use for clustering
        # Choices:
        # 'MV' -> megavoxel frequencies,
        # 'Texture_Features' -> 4 haralick texture features,
        # 'Combined' -> both together

        image_feature_data = pd.read_csv(self.feature_file[0], sep='\t', na_values='        NaN')

        # Identify columns
        columns = image_feature_data.columns
        mv_cols = columns[columns.map(lambda col: col.startswith('MV'))]
        # all columns corresponding to megavoxel categories #should usually be -4 since contrast is still included here.
        texture_cols = columns[columns.map(lambda col: col.startswith('text_'))]
        featurecols = columns[columns.map(lambda col: col.startswith('MV') or col.startswith('text_'))]
        mdatacols = columns.drop(featurecols)
        # drop duplicate data rows:
        image_feature_data.drop_duplicates(subset=featurecols, inplace=True)

        # remove non-finite/ non-scalar valued rows in both
        image_feature_data = image_feature_data[np.isfinite(image_feature_data[featurecols]).all(1)]
        image_feature_data.sort_values(list(featurecols), axis=0, inplace=True)

        # min-max scale all data and split to feature and metadata
        mind = np.min(image_feature_data[featurecols], axis=0)
        maxd = np.max(image_feature_data[featurecols], axis=0)

        if np.array_equal(mind, maxd) == False:
            featuredf = (image_feature_data[featurecols] - mind) / (maxd - mind)
            mdatadf = image_feature_data[mdatacols]
            featuredf.dropna(axis=0, inplace=True)  # thresh=int(0.2 * featuredf.shape[0]) )

            # select data
            if len(self.filt) == 1:
                if self.filt[0] == 'MV':
                    X = featuredf[mv_cols].to_numpy().astype(np.float64)
                elif self.filt[0] == 'Texture_Features':
                    X = featuredf[texture_cols].to_numpy().astype(np.float64)
            elif self.filt == ['MV', 'Texture_Features']:
                X = featuredf.to_numpy().astype(np.float64)
            else:
                X = featuredf[mv_cols].to_numpy().astype(np.float64)
                print('Invalid data set choice. Using Megavoxel frequencies.')
            print('Dataset shape:', X.shape)
            self.filtered_data = X

            # reset imageIDs
            self.imageIDs.clear()
            self.imageIDs.extend(np.array(mdatadf['ImageID'], dtype='object').astype(int))
            # reset labels
            z = np.ones(X.shape[0]).astype(int)
            if filter_data != "No Grouping":
                z = np.array(mdatadf[filter_data], dtype='object')
            self.labels.clear()
            self.labels.extend(list(map(str, z)))
            # misc info
            numMVperImg = np.array(image_feature_data['NumMV']).astype(np.float64)
            num_images_kept = X.shape[0]
            print(f'\nNumber of images: {num_images_kept}\n')
            result_plot(self, X, projection, plot, new_plot)
        else:
            errorWindow('Feature File Data Error', 'Check if have more than 1 row of data and that min and max values are not the same')
    def setnumcluster(self, group):
        clustnum=Clustering.setcluster(self.numcluster, self.filtered_data, self.plot_data, np.array(self.labels), group)
        self.numcluster=clustnum.clust
# end resultsWindow
