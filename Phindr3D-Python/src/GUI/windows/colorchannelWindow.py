from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np

class colorchannelWindow(object):
    def __init__(self, ch, color, win_title, col_title, labels):
        #main layout
        win = QDialog()
        win.setWindowTitle(win_title)
        title = QLabel(col_title)
        title.setFont(QFont('Arial', 25))
        title.setAlignment(Qt.AlignCenter)
        win.setLayout(QVBoxLayout())
        win.layout().addWidget(title)
        #label button layout
        button_box = QGroupBox(title)
        btn_layout=QVBoxLayout()
        self.btn=[]
        btn_grp = QButtonGroup()
        btn_grp.setExclusive(True)
        #ok/cancel button layout
        confirm_layout=QHBoxLayout()
        btn_ok= QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        confirm_layout.addWidget(btn_ok)
        confirm_layout.addWidget(btn_cancel)
        #color setup
        self.color=color
        self.tmp_color=color[:]
        #add label buttons
        for i in range(ch):
            self.btn.append(QPushButton(labels[i]))
            #channel button colour is colour of respective channel
            self.btn[i].setStyleSheet('background-color: rgb' +str(tuple((np.array(self.color[i])*255).astype(int))) +';')
            btn_layout.addWidget(self.btn[i])
            btn_grp.addButton(self.btn[i], i+1)
        button_box.setLayout(btn_layout)
        win.layout().addWidget(button_box)
        #add scrollbar for labels
        scrollArea = QScrollArea()
        scrollArea.setWidget(button_box)
        scrollArea.setWidgetResizable(True)
        win.layout().addWidget(scrollArea)
        win.layout().addLayout(confirm_layout)
        #button callbacks
        btn_grp.buttonPressed.connect(self.colorpicker_window)
        btn_ok.clicked.connect(lambda: self.confirmed_colors(win))
        btn_cancel.clicked.connect(lambda: win.close())
        #window size
        minsize = win.minimumSizeHint()
        minsize.setHeight(win.minimumSizeHint().height() + 100)
        minsize.setWidth(win.minimumSizeHint().width() + 100)
        win.setFixedSize(minsize)

        win.show()
        win.setWindowFlags(win.windowFlags() | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        win.exec()

    def colorpicker_window(self, button):
            #Qt custom Colorpicker. Update channel button and current colour to selected colour. Update channel color list.
            wincolor=QColorDialog()
            btn_num=0
            for btns in range(len(self.btn)):
                if self.btn[btns].text()==button.text():
                    btn_num=btns
                    break
            curcolor = (np.array(self.tmp_color[btn_num]) * 255).astype(int)
            wincolor.setCurrentColor(QColor.fromRgb(curcolor[0], curcolor[1], curcolor[2]))
            wincolor.exec_()
            rgb_color = wincolor.selectedColor()
            if rgb_color.isValid():
                self.btn[btn_num].setStyleSheet('background-color: rgb' +str(rgb_color.getRgb()[:-1]) +';')
                self.tmp_color[btn_num] = np.array(rgb_color.getRgb()[:-1]) / 255
    def confirmed_colors(self, win):
        self.color=self.tmp_color[:]
        win.close()