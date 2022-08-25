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
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
from ..GUI.windows.helperclasses import *

class TrainingFunctions:
    """Static methods for training. Referenced from
    https://github.com/DWALab/Phindr3D/tree/9b95aebbd2a62c41d3c87a36f1122a78a21019c8/Lib
    and
    https://github.com/SRI-RSST/Phindr3D-python/blob/ba588bc925ef72c72103738d17ea922d20771064/phindr_functions.py
    No constructor. All parameters and methods are static.
    """
    @staticmethod
    def partition_data(mv_data, grps, select_grps):
        train_mv=[]
        train_lbl=[]
        train_ind=[]
        #for selected class split into 60/40 (train/test)
        for grp in select_grps:
            idx=np.array(np.where(grps==grp)[0], dtype=int)
            X_train, X_test, y_train, y_test, ind_train, ind_test = train_test_split(mv_data[idx], grps[idx],idx,test_size = 0.4)#, random_state = 0) #random_state -> seed
            train_mv.extend(X_train)
            train_lbl.extend(y_train)
            train_ind.extend(ind_train)
        #test data & indices
        test_mv = np.delete(mv_data[:], train_ind, axis= 0)
        test_ind= np.delete(np.linspace(0,np.shape(mv_data)[0]-1, num=np.shape(mv_data)[0], dtype=int), train_ind, axis=0)
        return(train_mv, train_lbl, test_mv, test_ind)
    #get classifier predictions of selected classes
    @staticmethod
    def random_forest_model(X_train, y_train, X_test, test_classes):
        clf = RandomForestClassifier(n_estimators=500, bootstrap=True)
        clf.fit(X_train, y_train)
        labels=clf.predict(X_test)
        class_table = pd.crosstab(index=test_classes,columns=labels)
        class_table.index.name = None
        return(class_table)
    def selectclasses(self, mv, lbls):
        select_grps=[]
        if len(np.unique(lbls))>1:
            win=selectWindow(np.unique(lbls), "", "Select Classes", "Classes", "", select_grps)
            if win.x_press:
                print("Cancelled")
            elif len(select_grps)>1:
                pts=[len(np.array(np.where(lbls==grp)[0], dtype=int)) for grp in select_grps]
                if min(pts)>1:
                    X_train, y_train, X_test, y_test= self.partition_data(mv, lbls, select_grps)
                    class_tbl=self.random_forest_model(X_train, y_train, X_test, lbls[y_test])
                    #export classification table
                    name = QFileDialog.getSaveFileName(None, 'Save File')[0]
                    if name:
                        class_tbl.to_csv(name, sep='\t', mode='w')
                else:
                    grp_check=np.array(select_grps)
                    grp_check=grp_check[np.where(np.array(pts) < 2)[0]]
                    errorWindow("Select Classes", "There are classes with less than 2 data points. Classes with less than 2 data points '{}'".format(grp_check))
            else:
                errorWindow("Select Classes", "Must select at least two classes. Selected Class '{}'".format(select_grps))
        else:
            errorWindow("Select Classes", "Must have at least two classes. Only has one class {}".format(np.unique(lbls)))



# end TrainingFunctions


