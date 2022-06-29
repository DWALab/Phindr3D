from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import matplotlib
from .helperclasses import MplCanvas

#Callback will open image associated with data point. Note: in 3D plot pan is hold left-click swipe, zoom is hold right-click swipe
class interactive_click():
    def __init__(self, main_plot, plots, projection, x, y, z, labels, feature_file, color):
        self.main_plot=main_plot
        self.plots=plots
        self.projection=projection
        self.x=x
        self.y=y
        self.z=z
        self.labels=labels
        self.feature_file=feature_file
        self.color=color

    def buildImageViewer(self, x_data, label, cur_label, index, color, feature_file):
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
        adjustbar.setFixedWidth(50)
        adjustbar.setStyleSheet(
            "QSlider::groove:vertical {background-color: #8DE8F6; border: 1px solid;height: 700px;margin: 0px;}"
            "QSlider::handle:vertical {background-color: #8C8C8C; border: 1px silver; height: 30px; width: 10px; margin: -5px 0px;}")

        #parent layout
        grid.addLayout(info_box, 0, 0)
        grid.addWidget(main_plot, 0, 1)
        grid.addWidget(pjt_box, 1, 1, Qt.AlignCenter)
        grid.addWidget(adjustbar, 0, 2)

        win.setLayout(grid)

        self.channel_display(adjustbar, main_plot, color, x_data, label, cur_label, index, feature_file, file_info, ch_info)
        win.show()
        win.exec()