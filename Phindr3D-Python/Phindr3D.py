# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of Phindr3D <https://github.com/DWALab/Phindr3D>.
#
# Phindr3D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Phindr3D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Phindr3D.  If not, see <http://www.gnu.org/licenses/>.

from os import path
from src import *

def run_mainGUI(iconFile):
    """Create an instance of MainGUI and run the application."""
    app = QApplication(sys.argv)
    window = MainGUI(iconFile)
    window.show()
    app.exec()

if __name__ == '__main__':
    """Phindr3D is designed for automated cell phenotype analysis."""
    iconFile = path.abspath(path.join(path.dirname(__file__), 'phindr3d_icon.png'))

    # Start the GUI found in src/GUI/MainGUI.py
    run_mainGUI(iconFile)

# end main
