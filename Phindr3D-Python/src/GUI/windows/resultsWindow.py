from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import proj3d
from matplotlib import rcParams, cycler
import matplotlib.colors as mcolors
from .interactive_click import interactive_points
import pandas as pd
from math import ceil, floor
from .featurefilegroupingwindow import featurefilegroupingWindow
from textwrap import wrap, fill
from .helperclasses import MplCanvas
from ... Clustering import *

class resultsWindow(QDialog):
    def __init__(self, color):
        super(resultsWindow, self).__init__()
        self.setWindowTitle("Results")
        self.feature_file=[]
        self.imageIDs=[]
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
        rotation = plotproperties.addAction("3D Rotation")
        reset_action = QAction("Reset Plot View", self)
        reset_action.triggered.connect(lambda: self.reset_view())
        resetview = plotproperties.addAction(reset_action)

        # menu features go here

        # defining widgets
        box = QGroupBox()
        boxlayout = QGridLayout()
        selectfile = QPushButton("Select Feature File")
        map_type = QComboBox()
        map_type.addItem("PCA")
        map_type.addItem("t-SNE")
        map_type.addItem("Sammon")
        twod = QCheckBox("2D")
        threed = QCheckBox("3D")
        dimensionbox = QGroupBox()
        dimensionboxlayout = QHBoxLayout()
        dimensionboxlayout.addWidget(twod)
        dimensionboxlayout.addWidget(threed)
        dimensionbox.setLayout(dimensionboxlayout)
        colordropdown = QComboBox()
        boxlayout.addWidget(selectfile, 0, 0, 3, 1)
        boxlayout.addWidget(QLabel("Plot Type"), 0, 1, 1, 1)
        boxlayout.addWidget(map_type, 1, 1, 1, 1)
        boxlayout.addWidget(dimensionbox, 2, 1, 1, 1)
        boxlayout.addWidget(QLabel("Color By"), 0, 2, 1, 1)
        boxlayout.addWidget(colordropdown, 1, 2, 1, 1)
        box.setLayout(boxlayout)
        #menu actions activated
        inputfile.triggered.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText()))
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        # test points. normally empty list x=[], y=[], z=[] #temporary until read in formated super/megavoxel data
        #x = [1, 5]
        #y = [7, 2]
        #z = [0,0]
        # if !self.foundMetadata:  #x and y coordinates from super/megavoxels
        self.plot_data = []
        self.labels = []
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter3D([], [], [], s=10, alpha=1, depthshade=False)  # , picker=True)
        self.main_plot.axes.set_position([-0.25, 0.1, 1, 1])
        if not self.plot_data:
            self.main_plot.axes.set_ylim(bottom=0)
            self.main_plot.axes.set_xlim(left=0)
        self.original_xlim = sc_plot.axes.get_xlim3d()
        self.original_ylim = sc_plot.axes.get_ylim3d()
        self.original_zlim = sc_plot.axes.get_zlim3d()
        self.projection = "2d"  # update from radiobutton

        def toggle_2d_3d(data, sc_plot, checkbox_cur, checkbox_prev, dim, plot):
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            check_projection(data, sc_plot, dim, plot)

        def check_projection(data, sc_plot, dim, plot):
            if dim == "2d":
                self.projection = dim
                self.main_plot.axes.mouse_init()
                self.main_plot.axes.view_init(azim=-90, elev=89)
                self.main_plot.axes.get_zaxis().line.set_linewidth(0)
                self.main_plot.axes.tick_params(axis='z', labelsize=0)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()
            elif dim == "3d":
                self.projection = dim
                self.main_plot.axes.get_zaxis().line.set_linewidth(1)
                self.main_plot.axes.tick_params(axis='z', labelsize=10)
                self.main_plot.fig.canvas.draw()
                self.main_plot.axes.mouse_init()
            if self.feature_file and colordropdown.count() > 0:
                self.data_filt(colordropdown, "False", self.projection, plot, True)

        # button features go here
        selectfile.clicked.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText()))
        twod.toggled.connect(lambda: toggle_2d_3d(self.plot_data, sc_plot, twod, threed, "2d", map_type.currentText()))
        threed.toggled.connect(
            lambda: toggle_2d_3d(self.plot_data, sc_plot, threed, twod, "3d", map_type.currentText()))
        twod.setChecked(True)
        picked_pt = interactive_points(self.main_plot, self.projection, self.plot_data, self.labels, self.feature_file,
                                       color, self.imageIDs)
        # matplotlib callback mouse/scroller actions
        cid = self.main_plot.fig.canvas.mpl_connect('pick_event', picked_pt)
        colordropdown.currentIndexChanged.connect(
            lambda: self.data_filt(colordropdown, "False", self.projection, map_type.currentText(),
                                   False) if self.feature_file and colordropdown.count() > 0 else None)
        map_type.currentIndexChanged.connect(
            lambda: self.data_filt(colordropdown, "False", self.projection, map_type.currentText(),
                                   True) if self.feature_file and colordropdown.count() > 0 else None)
        # building layout
        layout = QGridLayout()
        toolbar = NavigationToolbar(self.main_plot, self)

        layout.addWidget(toolbar, 0, 0, 1, 1)
        layout.addWidget(self.main_plot, 1, 0, 1, 1)
        layout.addWidget(box, 2, 0, 1, 1)
        layout.setMenuBar(menubar)
        self.setLayout(layout)
        minsize = self.minimumSizeHint()
        minsize.setHeight(self.minimumSizeHint().height() + 600)
        minsize.setWidth(self.minimumSizeHint().width() + 600)
        self.setFixedSize(minsize)

    def reset_view(self):
        self.main_plot.axes.set_xlim3d(self.original_xlim)
        self.main_plot.axes.set_ylim3d(self.original_ylim)
        self.main_plot.axes.set_zlim3d(self.original_zlim)
        self.main_plot.axes.view_init(azim=-90, elev=89)
        self.main_plot.draw()

    def loadFeaturefile(self, grouping, plot):
        filename, dump = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
        if filename != '':
            self.feature_file.clear()
            self.feature_file.append(filename)
            print(self.feature_file)

            self.data_filt(grouping, True, self.projection, plot, True)
        else:
            load_featurefile_win = self.buildErrorWindow("Select Valid Feature File (.txt)", QMessageBox.Critical)
            load_featurefile_win.exec()

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def data_filt(self, grouping, load, projection, plot, new_plot): #modified from Phindr...
        image_feature_data_raw = pd.read_csv(self.feature_file[0], sep='\t', na_values='        NaN')
        if load==True:
            grouping.blockSignals(True)
            if grouping.count()>1:
                grouping.clear()
            grps=[]
            featurefilegroupingWindow(image_feature_data_raw.columns, grps)
            grouping.addItem("No Grouping")
            for col in grps:
                grouping.addItem(col)
            grouping.blockSignals(False)
        filter_data= grouping.currentText()

        # rescale texture features to the range [0, 1]
        rescale_texture_features = False

        # choose dataset to use for clustering: EDIT HERE
        # Choices:
        # 'MV' -> megavoxel frequencies,
        # 'text' -> 4 haralick texture features,
        # 'combined' -> both together
        datachoice = 'MV'
        image_feature_data = image_feature_data_raw

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
        featuredf = (image_feature_data[featurecols] - mind) / (maxd - mind)
        mdatadf = image_feature_data[mdatacols]

        # select data
        if datachoice.lower() == 'mv':
            X = featuredf[mv_cols].to_numpy().astype(np.float64)
        elif datachoice.lower() == 'text':
            X = featuredf[texture_cols].to_numpy().astype(np.float64)
        elif datachoice.lower() == 'combined':
            X = featuredf.to_numpy().astype(np.float64)
        else:
            X = featuredf[mv_cols].to_numpy().astype(np.float64)
            print('Invalid data set choice. Using Megavoxel frequencies.')
        print('Dataset shape:', X.shape)
        self.imageIDs.clear()
        self.imageIDs.extend(np.array(mdatadf['ImageID'], dtype='object').astype(int))
        z=np.ones(X.shape[0]).astype(int)
        if filter_data!="No Grouping":
            z=np.array(mdatadf[filter_data], dtype='object')
        numMVperImg = np.array(image_feature_data['NumMV']).astype(np.float64)
        # misc info
        num_images_kept = X.shape[0]
        print(f'\nNumber of images: {num_images_kept}\n')

        if new_plot:
            self.main_plot.axes.clear()
            dim=int(projection[0])
            #send to clustering.py for PCA, Sammon, t-SNE analysis
            title, xlabel, ylabel, P=plot_type(X, dim, plot)
            self.plot_data.clear()

            #save new x, y, z data and plot
            self.plot_data.append(P[:,0])
            self.plot_data.append(P[:,1])
            if dim==3:
                self.plot_data.append(P[:, 2])
            else:
                self.plot_data.append(np.zeros(len(self.plot_data[-1])))
        else:
            for artist in self.main_plot.axes.collections:
                artist.remove()
        self.labels.clear()
        self.labels.extend(list(map(str, z)))
        #plot data
        colors= plt.cm.get_cmap('gist_ncar')(range(0, 255, floor(255/len(np.unique(self.labels)))))
        plots=[]
        if len(np.unique(self.labels))>1:
            for label, i in zip(np.unique(self.labels), range(len(np.unique(self.labels)))):
                plots.append(self.main_plot.axes.scatter3D(self.plot_data[0][np.array(self.labels)==label], self.plot_data[1][np.array(self.labels)==label], self.plot_data[2][np.array(self.labels)==label], label=label,
                             s=10, alpha=1, color=[colors[i]], depthshade=False, picker=2, cmap=colors))
        else:
            plots.append(self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], label=self.labels[0],
                                              s=10, alpha=1, color=[colors[0]], depthshade=False, picker=2, cmap=colors))
        #legend formating
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
            labels = [fill(l, 20) for l in np.unique(self.labels)]
            self.main_plot.axes.legend(handle, labels, bbox_to_anchor=bbox, ncol=cols,loc='center right')
        else:
            self.main_plot.axes.legend(handle, np.unique(self.labels),bbox_to_anchor=bbox, ncol=cols,loc='center right')
        if new_plot:
            self.main_plot.axes.set_title(title)
            self.main_plot.axes.set_xlabel(xlabel)
            self.main_plot.axes.set_ylabel(ylabel)
            #save original x,y,z axis limits for resetview
            for plot in plots:
                self.original_xlim=[min(plot.axes.get_xlim3d()[0], self.original_xlim[0]), max(plot.axes.get_xlim3d()[1], self.original_xlim[1])]
                self.original_ylim=[min(plot.axes.get_ylim3d()[0], self.original_ylim[0]), max(plot.axes.get_ylim3d()[1], self.original_ylim[1])]
                self.original_zlim=[min(plot.axes.get_zlim3d()[0], self.original_zlim[0]), max(plot.axes.get_zlim3d()[1], self.original_zlim[1])]
        self.main_plot.draw()
# end resultsWindow