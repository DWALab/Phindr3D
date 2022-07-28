from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import proj3d
from matplotlib import rcParams, cycler
from .interactive_click import interactive_points
import pandas as pd
from .featurefilegroupingwindow import featurefilegroupingWindow
from .helperclasses import MplCanvas
from .plot_functions import *
#from Clustering import *
#from ...Clustering.__init__ import *
#try:
#    from ...Clustering.Clustering_Functions import *
#except ImportError:
#    from src.Clustering.Clustering_Functions import *
class resultsWindow(QDialog):
    def __init__(self, color):
        super(resultsWindow, self).__init__()
        self.setWindowTitle("Results")
        self.feature_file=[]
        self.imageIDs=[]
        self.plots=[]
        self.filtered_data=0
        menubar = QMenuBar()
        file = menubar.addMenu("File")
        inputfile = file.addAction("Input Feature File")
        data = menubar.addMenu("Data Analysis")
        classification = data.addMenu("Classification")
        selectclasses = classification.addAction("Select Classes")
        clustering = data.addMenu("Clustering")
        estimate = clustering.addAction("Estimate Clusters")
        estimate.triggered.connect(lambda: Clustering().clusterest(self.filtered_data) if len(self.plot_data)>0 else None)
        setnumber = clustering.addAction("Set Number of Clusters")
        piemaps = clustering.addAction("Pie Maps")
        export = clustering.addAction("Export Cluster Results")
        plotproperties = menubar.addMenu("Plot Properties")
        rotation_enable = plotproperties.addAction("3D Rotation Enable")
        rotation_enable.triggered.connect(lambda: self.main_plot.axes.mouse_init())
        rotation_disable = plotproperties.addAction("3D Rotation Disable")
        rotation_disable.triggered.connect(lambda: self.main_plot.axes.disable_mouse_rotation())
        reset_action = QAction("Reset Plot View", self)
        reset_action.triggered.connect(lambda: reset_view(self))
        resetview = plotproperties.addAction(reset_action)

        # menu features go here

        # defining widgets
        box = QGroupBox()
        boxlayout = QGridLayout()
        selectfile = QPushButton("Select Feature File")
        prevdata = QPushButton("Import Previous Plot Data")
        exportdata = QPushButton("Export Plot Data")
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
        boxlayout.addWidget(prevdata, 2, 0, 1, 1)
        boxlayout.addWidget(exportdata, 3, 0, 1, 1)
        boxlayout.addWidget(QLabel("Plot Type"), 0, 1, 1, 1)
        boxlayout.addWidget(map_type, 1, 1, 1, 1)
        boxlayout.addWidget(dimensionbox, 2, 1, 1, 1)
        boxlayout.addWidget(cmap, 2, 2, 1, 1)
        boxlayout.addWidget(QLabel("Color By"), 0, 2, 1, 1)
        boxlayout.addWidget(colordropdown, 1, 2, 1, 1)
        box.setLayout(boxlayout)
        #menu actions activated
        inputfile.triggered.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText(), True))
        exportdata.clicked.connect(lambda: save_file(self, map_type.currentText()))
        prevdata.clicked.connect(lambda: import_file(self, map_type, colordropdown, twod, threed))
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        self.plot_data = []
        self.labels = []
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter3D([], [], [], s=10, alpha=1, depthshade=False)  # , picker=True)
        self.main_plot.axes.set_position([-0.25, -0.05, 1, 1])
        #self.main_plot.fig.canvas.setFocusPolicy(Qt.ClickFocus)
        #self.main_plot.fig.canvas.setFocus()
        if not self.plot_data:
            self.main_plot.axes.set_ylim(bottom=0)
            self.main_plot.axes.set_xlim(left=0)
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
                self.data_filt(colordropdown, self.projection, plot, True)

        # button features and callbacks
        selectfile.clicked.connect(lambda: self.loadFeaturefile(colordropdown, map_type.currentText(), True))
        cmap.clicked.connect(lambda: legend_colors(self) if len(self.labels)>0 else None)
        twod.toggled.connect(lambda: toggle_2d_3d(twod, threed, "2d", map_type.currentText()))
        threed.toggled.connect(lambda: toggle_2d_3d(threed, twod, "3d", map_type.currentText()))
        twod.setChecked(True)
        picked_pt=interactive_points(self.main_plot, self.projection, self.plot_data, self.labels, self.feature_file, color, self.imageIDs)
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
            self.feature_file.clear()
            self.feature_file.append(filename)
            print(self.feature_file)
            grouping=self.color_groupings(grouping)
            self.data_filt(grouping, self.projection, plot, new_plot)
        else:
            load_featurefile_win = self.buildErrorWindow("Select Valid Feature File (.txt)", QMessageBox.Critical)
            load_featurefile_win.exec()

    def color_groupings(self, grouping):
        feature_data = pd.read_csv(self.feature_file[0], sep='\t', na_values='        NaN')
        grouping.blockSignals(True)
        grps=[]
        featurefilegroupingWindow(feature_data.columns, grps)
        grouping.clear()
        grouping.addItem("No Grouping")
        for col in grps:
            grouping.addItem(col)
        grouping.blockSignals(False)
        return(grouping)
    def data_filt(self, grouping, projection, plot, new_plot):
        filter_data= grouping.currentText()
        print(filter_data)
        # rescale texture features to the range [0, 1]
        rescale_texture_features = False

        # choose dataset to use for clustering: EDIT HERE
        # Choices:
        # 'MV' -> megavoxel frequencies,
        # 'text' -> 4 haralick texture features,
        # 'combined' -> both together
        datachoice = 'MV'
        image_feature_data = pd.read_csv(self.feature_file[0], sep='\t', na_values='        NaN')

        # Identify columns
        columns = image_feature_data.columns
        mv_cols = columns[columns.map(lambda col: col.startswith('MV'))]
        # all columns corresponding to megavoxel categories #should usually be -4 since contrast is still included here.
        texture_cols = columns[columns.map(lambda col: col.startswith('text_'))]
        featurecols = columns[columns.map(lambda col: col.startswith('MV') or col.startswith('text_'))]
        mdatacols = columns.drop(featurecols)

        # drop duplicate data rows:
        #image_feature_data.drop_duplicates(subset=featurecols, inplace=True)


        # remove non-finite/ non-scalar valued rows in both
        #image_feature_data = image_feature_data[np.isfinite(image_feature_data[featurecols]).all(1)]
        #image_feature_data.sort_values(list(featurecols), axis=0, inplace=True)

        # min-max scale all data and split to feature and metadata
        mind = np.min(image_feature_data[featurecols], axis=0)
        maxd = np.max(image_feature_data[featurecols], axis=0)
        print(mind, maxd)
        featuredf = (image_feature_data[featurecols] - mind) / (maxd - mind)
        mdatadf = image_feature_data[mdatacols]
        featuredf.dropna(axis=0, thresh=int(0.2 * featuredf.shape[0]), inplace=True)

        np.savetxt('/home/kjok/phindr_matlab_numpy/datarawPY.txt', featuredf.to_numpy().astype(np.float64))

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
        np.savetxt('/home/kjok/phindr_matlab_numpy/dataPy.txt', X)
        self.filtered_data=X
        #reset imageIDs
        self.imageIDs.clear()
        self.imageIDs.extend(np.array(mdatadf['ImageID'], dtype='object').astype(int))
        #reset labels
        z=np.ones(X.shape[0]).astype(int)
        if filter_data!="No Grouping":
            z=np.array(mdatadf[filter_data], dtype='object')
        self.labels.clear()
        self.labels.extend(list(map(str, z)))
        # misc info
        numMVperImg = np.array(image_feature_data['NumMV']).astype(np.float64)
        num_images_kept = X.shape[0]
        print(f'\nNumber of images: {num_images_kept}\n')
        result_plot(self, X, projection, plot, new_plot)
    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert
# end resultsWindow