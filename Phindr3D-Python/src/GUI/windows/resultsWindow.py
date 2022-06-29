from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
from sklearn.decomposition import PCA, KernelPCA
from sklearn.preprocessing import StandardScaler
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import proj3d
from matplotlib import rcParams, cycler
from .interactive_click import interactive_click
import pandas as pd
from .featurefilegroupingwindow import featurefilegroupingWindow
from textwrap import wrap, fill
from .helperclasses import MplCanvas



class resultsWindow(QDialog):
    def __init__(self, color):
        super(resultsWindow, self).__init__()
        self.setWindowTitle("Results")
        self.feature_file=[]
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
        typedropdown = QComboBox()
        typedropdown.addItem("PCA")
        typedropdown.addItem("t-SNE")
        typedropdown.addItem("Sammon")
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
        boxlayout.addWidget(typedropdown, 1, 1, 1, 1)
        boxlayout.addWidget(dimensionbox, 2, 1, 1, 1)
        boxlayout.addWidget(QLabel("Color By"), 0, 2, 1, 1)
        boxlayout.addWidget(colordropdown, 1, 2, 1, 1)
        box.setLayout(boxlayout)
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        # test points. normally empty list x=[], y=[], z=[] #temporary until read in formated super/megavoxel data
        #x = [1, 5]
        #y = [7, 2]
        #z = [0,0]
        # if !self.foundMetadata:  #x and y coordinates from super/megavoxels
        self.x=[]
        self.y=[]
        self.z=[]
        self.labels=[]
        self.plots=[]
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter3D(self.x, self.y, self.z, s=10, alpha=1, depthshade=False)#, picker=True)
        self.main_plot.axes.set_position([-0.25, 0.1, 1, 1])
        if not self.x and not self.y:
            self.main_plot.axes.set_ylim(bottom=0)
            self.main_plot.axes.set_xlim(left=0)
        self.original_xlim=0
        self.original_ylim=0

        if all(np.array(self.z)==0):
            self.original_zlim=[0, 0.1]
        else:
            self.original_zlim=sc_plot.axes.get_zlim3d()

        self.projection = "2d"  # update from radiobutton
        def axis_limit(sc_plot):
            xlim = sc_plot.axes.get_xlim3d()
            ylim = sc_plot.axes.get_ylim3d()
            lower_lim=min(xlim[0], ylim[0])
            upper_lim=max(xlim[1], ylim[1])
            return(lower_lim, upper_lim)
        def toggle_2d_3d(x, y, z, sc_plot, checkbox_cur, checkbox_prev, dim):
            if checkbox_cur.isChecked() and checkbox_prev.isChecked():
                checkbox_prev.setChecked(False)
            check_projection(x, y, z, sc_plot, dim)
        def check_projection(x, y, z, sc_plot, dim):
            if dim == "2d":
                self.projection=dim
                low, high= axis_limit(sc_plot)
                #for debugging
                #print(low, high)
                self.main_plot.axes.mouse_init()
                self.main_plot.axes.view_init(azim=-90, elev=-90)
                if self.original_xlim==0 and self.original_ylim==0 and self.original_zlim==0:
                    self.original_xlim=[low-1, high+1]
                    self.original_ylim=[low - 1, high + 1]
                self.main_plot.axes.set_xlim(low-1, high+1)
                self.main_plot.axes.set_ylim(low-1, high+1)
                self.main_plot.axes.get_zaxis().line.set_linewidth(0)
                self.main_plot.axes.tick_params(axis='z', labelsize=0)
                #self.main_plot.axes.set_zlim3d(0,0.1)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()
            elif dim == "3d":
                self.projection = dim
                self.main_plot.axes.get_zaxis().line.set_linewidth(1)
                if self.z:
                    self.main_plot.axes.set_zlim3d(np.amin(self.z)-1, np.amax(self.z)+1)
                self.main_plot.axes.tick_params(axis='z', labelsize=10)
                self.main_plot.fig.canvas.draw()
                self.main_plot.axes.mouse_init()
            if  self.feature_file and colordropdown.count()>0:
                self.data_filt(colordropdown, "False", self.projection)

        # button features go here
        selectfile.clicked.connect(lambda: self.loadFeaturefile(colordropdown))
        twod.toggled.connect(lambda: toggle_2d_3d(self.x, self.y, self.z, sc_plot, twod, threed, "2d"))
        threed.toggled.connect(lambda: toggle_2d_3d(self.x, self.y, self.z, sc_plot, threed, twod, "3d"))
        twod.setChecked(True)
        #fixed_camera = fixed_2d(self.main_plot, sc_plot, self.projection)
        picked_pt=interactive_click(self.main_plot, self.plots, self.projection, self.x, self.y, self.z, self.labels, self.feature_file, color)
        # matplotlib callback mouse/scroller actions
        cid=self.main_plot.fig.canvas.mpl_connect('pick_event', picked_pt)
        colordropdown.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, "False", self.projection) if self.feature_file and colordropdown.count()>0 else None)

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
        print(self.original_xlim, self.original_ylim, self.original_zlim)
        self.main_plot.axes.set_xlim(self.original_xlim)
        self.main_plot.axes.set_ylim(self.original_ylim)
        if self.z:
            self.main_plot.axes.set_zlim3d(np.amin(self.z) - 1, np.amax(self.z) + 1)
        #self.main_plot.axes.set_zlim3d(self.original_zlim)
        self.main_plot.axes.view_init(azim=-90, elev=-90)
        self.main_plot.draw()

    def loadFeaturefile(self, grouping):
        filename, dump = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
        if filename != '':
            self.feature_file.clear()
            self.feature_file.append(filename)
            print(self.feature_file)

            self.data_filt(grouping, True, "2d")
        else:
            load_featurefile_win = self.buildErrorWindow("Select Valid Feature File (.txt)", QMessageBox.Critical)
            load_featurefile_win.exec()

    def buildErrorWindow(self, errormessage, icon):
        alert = QMessageBox()
        alert.setWindowTitle("Error Dialog")
        alert.setText(errormessage)
        alert.setIcon(icon)
        return alert

    def data_filt(self, grouping, load, projection): #modified from Phindr... implemented PCA ...
        image_feature_data_raw = pd.read_csv(self.feature_file[0], sep='\t', na_values='        NaN')
        if load==True:
            if grouping.count()>0:
                grouping.clear()
            grps=[]
            featurefilegroupingWindow(image_feature_data_raw.columns, grps)
            grouping.addItem("No Grouping")
            #grouping.setCurrentIndex(0)
            for col in grps:
                grouping.addItem(col)

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
        mv_cols = columns[columns.map(lambda col: col.startswith(
            'MV'))]  # all columns corresponding to megavoxel categories #should usually be -4 since contrast is still included here.
        texture_cols = columns[columns.map(lambda col: col.startswith('text_'))]
        featurecols = columns[columns.map(lambda col: col.startswith('MV') or col.startswith('text_'))]
        mdatacols = columns.drop(featurecols)

        # drop  duplicate data rows:
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

        imageIDs = np.array(mdatadf['ImageID'], dtype='object')
        print(imageIDs)
        z=0
        cat=[1]
        if filter_data!="No Grouping":
            z=np.array(mdatadf[filter_data], dtype='object')
            cat=np.unique(z)

        numMVperImg = np.array(image_feature_data['NumMV']).astype(np.float64)
        y = imageIDs

        # misc info
        num_images_kept = X.shape[0]
        print(f'\nNumber of images: {num_images_kept}\n')

        # set colors if needed.
        if len(cat) > 20:
            #if len(Utreatments) > 10:

            colors= plt.cm.get_cmap('gist_rainbow')(range(0, 255, int(255/len(cat))))
            #color1 = plt.cm.get_cmap('tab20b')(np.linspace(0, 1, 20))
            #color2 = plt.cm.get_cmap('tab20c')(np.linspace(0, 1, 20))
            #colors = mcolors.LinearSegmentedColormap.from_list('my_colormap', np.vstack((color1, color2)))
            #colors=np.vstack((color1, color2))
            rcParams['axes.prop_cycle'] = cycler(color=colors)
        else:
            color1 = plt.cm.get_cmap('tab20')(np.linspace(0, 1, 20))
            rcParams['axes.prop_cycle'] = cycler(color=color1)


        # PCA kernel function: EDIT HERE
        # set as 'linear' for linear PCA, 'rbf' for gaussian kernel,
        # 'sigmoid' for sigmoid kernel,
        # 'cosine' for cosine kernel
        #func = 'rbf'
        func='linear'

        # plot parameters: EDIT HERE

        title = 'PCA plot'
        xlabel = 'PCA 1'
        ylabel = 'PCA 2'

        # makes plot


        sc = StandardScaler()
        X_show = sc.fit_transform(X)
        dim= int(projection[0])
        pca = KernelPCA(n_components= dim, kernel=func)
        P = pca.fit(X_show).transform(X_show)

        self.main_plot.axes.clear()
        self.plots.clear()
        self.x.clear()
        self.y.clear()
        self.z.clear()
        self.labels.clear()
        self.labels.extend(list(map(str, cat)))
        #save pca x, y, z data and plot
        for label, i in zip(cat, list(range(len(cat)))):
            if filter_data=="No Grouping":
                self.x.append(P[:,0])
                self.y.append(P[:,1])
                if dim==3:
                    self.z.append(P[:, 2])
                else:
                    self.z.append(np.zeros(len(self.x[-1])))
            else:
                self.x.append(P[z == label, 0])
                self.y.append(P[z == label, 1])
                if dim==3:
                    self.z.append(P[z == label, 2])
                else:
                    self.z.append(np.zeros(len(self.x[-1])))

            self.plots.append(self.main_plot.axes.scatter3D(self.x[-1], self.y[-1], self.z[-1], label=label,
                             s=10, alpha=0.7, depthshade=False, picker=0.1))
        #legend formating
        cols=2
        bbox=(1.3, 0.75)
        text=max(self.labels, key = len)
        if len(cat)>40:
            cols=4
            bbox=(1.6, 0.5)
        if len(text)>10:
            labels = [fill(l, 20) for l in self.labels]
            self.main_plot.axes.legend(labels, bbox_to_anchor=bbox, ncol=cols,loc='center right')
        else:
            self.main_plot.axes.legend(self.labels,bbox_to_anchor=bbox, ncol=cols,loc='center right')
        self.main_plot.axes.set_title(title)
        self.main_plot.axes.set_xlabel(xlabel)
        self.main_plot.axes.set_ylabel(ylabel)
        #self.main_plot.fig.tight_layout()
        self.main_plot.draw()
# end resultsWindow