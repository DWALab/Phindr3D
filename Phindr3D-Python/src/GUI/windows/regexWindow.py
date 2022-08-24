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
import re

class regexWindow(QDialog):
    def __init__(self):
        super(regexWindow, self).__init__()
        largetext = QFont("Arial", 12, 1)
        self.setWindowTitle("Create Regular Expression")
        self.samplefile = ""
        self.regex = r""
        layout = QGridLayout()

        samplelabel = QLabel()
        samplelabel.setText('Sample File Name:')
        samplelabel.setFixedSize(150, 30)

        self.samplefilebox = QTextEdit()
        self.samplefilebox.setReadOnly(True)
        self.samplefilebox.setPlaceholderText(self.samplefile)
        self.samplefilebox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.samplefilebox.setFont(largetext)
        self.samplefilebox.setFixedSize(450, 30)

        addGroup = QPushButton("Add Group")
        addGroup.setFixedSize(addGroup.minimumSizeHint())
        addGroup.setFixedHeight(30)

        groupbox = QLineEdit()
        groupbox.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        groupbox.setFont(largetext)
        groupbox.setFixedSize(200, 30)
        groupbox.setPlaceholderText("Group Name")

        viewlabel = QLabel()
        viewlabel.setText('Regex:')
        viewlabel.setFixedSize(50, 30)

        self.regexview = QTextEdit()
        self.regexview.setPlaceholderText(self.samplefile)
        self.regexview.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.regexview.setFont(largetext)
        self.regexview.setFixedSize(450, 30)

        finish = QPushButton("Finish")
        finish.setFixedSize(finish.minimumSizeHint())
        finish.setFixedHeight(30)

        cancel = QPushButton("Cancel")
        cancel.setFixedSize(cancel.minimumSizeHint())
        cancel.setFixedHeight(30)

        def addRegexGroup():
            filename = self.samplefilebox.toPlainText()
            cursor = self.samplefilebox.textCursor()
            selstart = cursor.selectionStart()
            selend = cursor.selectionEnd()
            groupValue = filename[selstart:selend]
            if selstart == 0:
                rematch = re.search(filename[selstart:selend+1], self.regex)
                restart = rematch.start()
                reend = rematch.end()-1
            else:
                rematch = re.search(filename[selstart-1:selend+1], self.regex)
                restart = rematch.start()+1
                reend = rematch.end()-1
            groupName = groupbox.text()
            if groupValue.isnumeric():
                grouplabel = f'(?P<{groupName}>\\d+)'
            else:
                grouplabel = f'(?P<{groupName}>.+)'

            self.regex = self.regex[:restart] + grouplabel + self.regex[reend:]
            self.regexview.setText(self.regex)
            groupbox.clear()
            groupbox.setPlaceholderText("Next Group Name")

        def finishRegex():
            self.regex = self.regexview.toPlainText()
            QDialog.accept(self)

        cancel.clicked.connect(self.close)
        finish.clicked.connect(finishRegex)
        addGroup.clicked.connect(addRegexGroup)

        layout.addWidget(samplelabel, 0, 0, 1, 1)
        layout.addWidget(self.samplefilebox, 0, 1, 1, 2)
        layout.addWidget(addGroup, 2, 1, 1, 1)
        layout.addWidget(groupbox, 2, 2, 1, 1)
        layout.addWidget(viewlabel, 3, 0, 1, 1)
        layout.addWidget(self.regexview, 3, 1, 1, 2)
        layout.addWidget(finish, 5, 0, 1, 1)
        layout.addWidget(cancel, 5, 1, 1, 1)
        self.setLayout(layout)
        self.setFixedSize(self.minimumSizeHint())

    def inputSampleFile(self):
        self.samplefilebox.setText(self.samplefile)
        self.regex = self.samplefile
        self.regexview.setText(self.regex)
