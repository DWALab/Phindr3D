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
        self.plots=[]
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
        prevdata = QPushButton("Import Previous Plot Data")
        exportdata = QPushButton("Export Plot Data")
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
        boxlayout.addWidget(prevdata, 2, 2, 1, 1)
        boxlayout.addWidget(exportdata, 3, 2, 1, 1)
        box.setLayout(boxlayout)
        #menu actions activated
        inputfile.triggered.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText(), True))
        exportdata.clicked.connect(lambda: self.save_file(map_type.currentText()))
        prevdata.clicked.connect(lambda: self.import_file(map_type, colordropdown, twod, threed))
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        self.plot_data = []
        self.labels = []
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter3D([], [], [], s=10, alpha=1, depthshade=False)  # , picker=True)
        self.main_plot.axes.set_position([-0.25, -0.05, 1, 1])
        self.main_plot.fig.canvas.setFocusPolicy(Qt.ClickFocus)
        self.main_plot.fig.canvas.setFocus()
        if not self.plot_data:
            self.main_plot.axes.set_ylim(bottom=0)
            self.main_plot.axes.set_xlim(left=0)
        self.original_xlim = sc_plot.axes.get_xlim3d()
        self.original_ylim = sc_plot.axes.get_ylim3d()
        self.original_zlim = sc_plot.axes.get_zlim3d()
        self.projection = "2d"  # update from radiobutton

        def toggle_2d_3d(checkbox_cur, checkbox_prev, dim, plot):
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            check_projection(dim, plot)
        #2d vs 3d settings
        def check_projection(dim, plot):
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
                self.main_plot.draw()
                self.main_plot.axes.mouse_init(rotate_btn=1, zoom_btn=[])
            if self.feature_file and colordropdown.count() > 0:
                self.data_filt(colordropdown, "False", self.projection, plot, True)

        # button features and callbacks
        selectfile.clicked.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText(), True))
        twod.toggled.connect(lambda: toggle_2d_3d(twod, threed, "2d", map_type.currentText()))
        threed.toggled.connect(lambda: toggle_2d_3d(threed, twod, "3d", map_type.currentText()))
        twod.setChecked(True)
        picked_pt=interactive_points(self.main_plot, self.projection, self.plot_data, self.labels, self.feature_file, color, self.imageIDs)
        self.main_plot.fig.canvas.mpl_connect('pick_event', picked_pt)
        colordropdown.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, "False", self.projection, map_type.currentText(),False) if self.feature_file and colordropdown.count() > 0 else None)
        map_type.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, "False", self.projection, map_type.currentText(),True) if self.feature_file and colordropdown.count() > 0 else None)
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

    def reset_view(self):
        self.main_plot.axes.set_xlim3d(self.original_xlim)
        self.main_plot.axes.set_ylim3d(self.original_ylim)
        self.main_plot.axes.set_zlim3d(self.original_zlim)
        self.main_plot.axes.view_init(azim=-90, elev=89)
        self.main_plot.draw()

    def loadFeaturefile(self, grouping, plot, new_plot):
        filename, dump = QFileDialog.getOpenFileName(self, 'Open Feature File', '', 'Text files (*.txt)')
        if filename != '':
            self.feature_file.clear()
            self.feature_file.append(filename)
            print(self.feature_file)
            self.data_filt(grouping, True, self.projection, plot, new_plot)
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
            #if grouping.count()>1:
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
            old_plots=self.plots[:]
            for plots in old_plots:
                plots.remove()
            for artist in self.main_plot.axes.collections:
                artist.remove()
        del self.plots[:]
        self.labels.clear()
        self.labels.extend(list(map(str, z)))
        #plot data
        colors= plt.cm.get_cmap('gist_ncar')(range(0, 255, floor(255/len(np.unique(self.labels)))))
        if len(np.unique(self.labels))>1:
            for label, i in zip(np.unique(self.labels), range(len(np.unique(self.labels)))):
                self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0][np.where(np.array(self.labels)==label)[0]], self.plot_data[1][np.where(np.array(self.labels)==label)[0]], self.plot_data[2][np.where(np.array(self.labels)==label)[0]], label=label,
                             s=10, alpha=1, color=[colors[i]], depthshade=False, picker=1.5, cmap=colors))
        else:
            self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], label=self.labels[0],
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
        self.main_plot.axes.set_title(plot + " Plot")
        self.main_plot.axes.set_xlabel(plot + " 1")
        self.main_plot.axes.set_ylabel(plot + " 2")
        if new_plot:
            #save original x,y,z axis limits for resetview
            self.original_xlim=[self.plots[-1].axes.get_xlim3d()[0], self.plots[-1].axes.get_xlim3d()[1]]
            self.original_ylim=[self.plots[-1].axes.get_ylim3d()[0], self.plots[-1].axes.get_ylim3d()[1]]
            self.original_zlim=[self.plots[-1].axes.get_zlim3d()[0], self.plots[-1].axes.get_zlim3d()[1]]
        self.main_plot.draw()
    #export current plot data
    def save_file(self, map):
        name = QFileDialog.getSaveFileName(self, 'Save File')[0]
        if name:
            for x in ['PCA','t-SNE','Sammon']:
                if (x in name) and x!=map:
                    name=name.replace(x, '')
            if name.find("txt")==-1:
                name=name+".txt"
            if name.find(map)==-1:
                name=name.replace(".txt", map+".txt")
            np.savetxt(name, np.concatenate((self.plot_data, self.original_xlim, self.original_ylim, self.original_zlim), axis=None), newline='', fmt='%10.5f')
    #import plot data
    def import_file(self, map_dropdown, colordropdown, twod, threed):
        filename= QFileDialog.getOpenFileName(self, 'Open Plot Data File', '', 'Text files (*.txt)')[0]
        if filename != '':
            print(filename)
            new_data = np.loadtxt(filename)
            self.original_xlim =[new_data[-6],new_data[-5]]
            self.original_ylim = [new_data[-4], new_data[-3]]
            self.original_zlim = [new_data[-2], new_data[-1]]
            self.reset_view()
            map=""
            if np.all(new_data[int((len(new_data)-6)/3):-6])!=0:
                threed.setChecked(True)
            else:
                twod.setChecked(True)
            self.plot_data.clear()
            self.plot_data.extend(np.array(new_data[:-6].reshape(3, int((len(new_data)-6)/3))))
            for x in ["PCA", "Sammon", "t-SNE"]:
                if x in filename:
                    map=x
                    map_dropdown.setCurrentIndex(map_dropdown.findText(map))
                    self.loadFeaturefile(colordropdown, map, False)
                    break
        else:
            load_datafile_win = self.buildErrorWindow("Select Valid Data File (.txt)", QMessageBox.Critical)
            load_datafile_win.exec()
# end resultsWindow