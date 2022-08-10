# These classes are not windows, but help build other features in windows
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

#matplotlib figure-plot creation
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=5, dpi=100, projection="3d"):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if projection=="3d":
            self.axes = self.fig.add_subplot(111, projection=projection)
        else:
            self.axes = self.fig.add_subplot(111, projection=None)
        super(MplCanvas, self).__init__(self.fig)
        self.cmap = None
    
    def setNearFull(self):
        self.axes.set_aspect('auto')
        self.axes.set_position([0.01, 0.01, 0.98, 0.98])
    

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
#selectclasses and featurefile checkbox window
class selectWindow(object):
    def __init__(self, chk_lbl, col_lbl, win_title, grp_title, col_title, groupings):
        win = QDialog()
        win.setWindowTitle(win_title)
        win.setLayout(QGridLayout())
        self.x_press=True
        ok_button = QPushButton("OK")

        # setup checkbox for groups
        if len(chk_lbl) > 0:
            #checkbox setup
            grp_title = QLabel(grp_title)
            grp_title.setFont(QFont('Arial', 10))
            grp_checkbox = QGroupBox()
            grp_checkbox.setFlat(True)
            grp_list = []
            grp_vbox = QVBoxLayout()
            grp_vbox.addWidget(grp_title)
            #select all button
            all_button=QPushButton("Select All")
            #add checkboxes to layout
            for lbl in chk_lbl:
                grp_list.append(QCheckBox(lbl))
                grp_vbox.addWidget(grp_list[-1])
            grp_vbox.addStretch(1)
            grp_checkbox.setLayout(grp_vbox)
            win.layout().addWidget(grp_checkbox, 0, 0)
            all_button.clicked.connect(lambda: [box.setChecked(True) for box in grp_list])
            ok_button.clicked.connect(lambda: self.selected(grp_checkbox, win, groupings))
            win.layout().addWidget(all_button, 1, 0)
            win.layout().addWidget(ok_button, 2, 0)
        else:
            ok_button.clicked.connect(lambda: win.close())
            win.layout().addWidget(ok_button, 1, 0)
        # setup Column box
        if len(col_lbl) > 0:
            ch_title = QLabel(col_title)
            ch_title.setFont(QFont('Arial', 10))
            ch_checkbox = QGroupBox()
            ch_checkbox.setFlat(True)
            ch_vbox = QVBoxLayout()
            ch_vbox.addWidget(ch_title)
            # add columns to layout
            for lbl in col_lbl:
                ch_label = QLabel(lbl)
                ch_vbox.addWidget(ch_label)
            ch_vbox.addStretch(1)
            ch_checkbox.setLayout(ch_vbox)
            win.layout().addWidget(ch_checkbox, 0, 1)
        #size window to fit all elements
        minsize = win.minimumSizeHint()
        minsize.setHeight(win.minimumSizeHint().height() + 100)
        minsize.setWidth(win.minimumSizeHint().width() + 100)
        win.setFixedSize(minsize)
        win.show()
        win.setWindowFlags(win.windowFlags() | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        win.exec()

    #return selected groups
    def selected(self, grp_checkbox, win, groupings):
        for checkbox in grp_checkbox.findChildren(QCheckBox):
            # print('%s: %s' % (checkbox.text(), checkbox.isChecked()))
            if checkbox.isChecked():
                groupings.append(checkbox.text())
        self.x_press=False
        win.close()