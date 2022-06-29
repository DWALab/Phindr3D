from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class featurefilegroupingWindow(object):
    def __init__(self, columns, groupings):
        win = QDialog()
        win.setWindowTitle("Filter Feature File Groups and Channels")
        win.setLayout(QFormLayout())

        grp_title = QLabel("Grouping")
        grp_title.setFont(QFont('Arial', 10))
        grp_checkbox=QGroupBox()
        grp_checkbox.setFlat(True)
        grp_list=[]
        grp_vbox = QVBoxLayout()
        grp_vbox.addWidget(grp_title)

        ch_title = QLabel("Channels")
        ch_title.setFont(QFont('Arial', 10))
        ch_checkbox=QGroupBox()
        ch_checkbox.setFlat(True)
        ch_vbox = QVBoxLayout()
        ch_vbox.addWidget(ch_title)

        for i in range (len(columns)):
            print(columns[i].find('Channel_'))
            if columns[i].find("Channel_")== 0:
                ch_label=QLabel(columns[i])
                ch_vbox.addWidget((ch_label))
            elif columns[i][:2].find("MV")== -1:
                grp_list.append(QCheckBox(columns[i]))
                grp_vbox.addWidget(grp_list[-1])

        grp_vbox.addStretch(1)
        grp_checkbox.setLayout(grp_vbox)

        ch_vbox.addStretch(1)
        ch_checkbox.setLayout(ch_vbox)

        win.layout().addRow(grp_checkbox, ch_checkbox)

        ok_button=QPushButton("OK")
        win.layout().addRow(ok_button)
        ok_button.clicked.connect(lambda :self.selected(grp_checkbox, win, groupings))

        win.show()
        win.exec()

    def selected(self, grp_checkbox, win, groupings):
        for checkbox in grp_checkbox.findChildren(QCheckBox):
            print('%s: %s' % (checkbox.text(), checkbox.isChecked()))
            if checkbox.isChecked():
                groupings.append(checkbox.text())
        win.close()