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

class MainGUI:
    """Defines the main GUI window of Phindr3D"""

    def __init__(self):
        """MainGUI constructor"""
        self.app = QApplication([])
        self.window = self.buildWindow()

    def buildWindow(self):
        """Build the window widget and its components"""
        win = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QPushButton('Top'))
        layout.addWidget(QPushButton('Bottom'))
        win.setLayout(layout)
        return win

    def run(self):
        """Show the window and run the application exec method to start the GUI"""
        self.window.show()
        self.app.exec()

# end class MainGUI