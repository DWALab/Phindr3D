from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np

class colorchannelWindow(object):
    def __init__(self, ch, color):
        win = QDialog()
        win.setWindowTitle("Color Channel Picker")
        title = QLabel("Channels")
        title.setFont(QFont('Arial', 25))
        title.setAlignment(Qt.AlignCenter)
        win.setLayout(QFormLayout())
        win.layout().addRow(title)
        self.btn=[]
        btn_grp = QButtonGroup()
        btn_grp.setExclusive(True)
        btn_ok= QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        self.color=color
        self.tmp_color=color[:]

        for i in range(ch):
            self.btn.append(QPushButton('Channel_' + str(i+1)))
            #channel button colour is colour of respective channel
            self.btn[i].setStyleSheet('background-color: rgb' +str(tuple((np.array(self.color[i])*255).astype(int))) +';')
            win.layout().addRow(self.btn[i])
            btn_grp.addButton(self.btn[i], i+1)
        print(btn_grp.buttons())
        win.layout().addRow(btn_ok, btn_cancel)
        btn_grp.buttonPressed.connect(self.colorpicker_window)
        btn_ok.clicked.connect(lambda: self.confirmed_colors(win, color))
        btn_cancel.clicked.connect(lambda: win.close())
        win.show()
        win.exec()

    def colorpicker_window(self, button):
            #Qt custom Colorpicker. Update channel button and current colour to selected colour. Update channel color list.
            wincolor=QColorDialog()
            curcolor = (np.array(self.tmp_color[int(button.text()[-1]) - 1]) * 255).astype(int)
            wincolor.setCurrentColor(QColor.fromRgb(curcolor[0], curcolor[1], curcolor[2]))
            wincolor.exec_()
            rgb_color = wincolor.selectedColor()
            if rgb_color.isValid():
                self.btn[int(button.text()[-1])-1].setStyleSheet('background-color: rgb' +str(rgb_color.getRgb()[:-1]) +';')
                self.tmp_color[int(button.text()[-1]) - 1] = np.array(rgb_color.getRgb()[:-1]) / 255
    def confirmed_colors(self, win, color):
        self.color=self.tmp_color[:]
        win.close()