# -*- coding: utf-8 -*-
import os
from PySide6 import QtWidgets, QtCore
from maya.app.general import mayaMixin
import maya.cmds as cmds
from importlib import *

class Gui(mayaMixin.MayaQWidgetBaseMixin, QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Dialog|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(os.path.splitext(os.path.basename(__file__))[0].replace('_', ' ').title().replace(' ', ''))
        self.ui_design()
    
    def ui_design(self):
        outputLayout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel("Joints :")
        self.check = QtWidgets.QCheckBox("Chain")
        self.spin = QtWidgets.QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMinimumWidth(40)
        self.spin.setMaximumWidth(40)
        self.button = QtWidgets.QPushButton("Insert")
        self.button.setMinimumWidth(100)
        self.button.setMaximumWidth(100)
        outputLayout.addWidget(self.label)
        outputLayout.addWidget(self.spin)
        outputLayout.addWidget(self.check)
        outputLayout.addWidget(self.button)
        self.setStyleSheet("font-weight:bold;")
        self.button.clicked.connect(self.insert_joints_between)  

    def insert_joints_between(self):
        cmds.undoInfo(openChunk=True)
        selection = cmds.ls(sl=True)
        if len(selection) == 2 and all(cmds.objectType(obj) == 'joint' for obj in selection) : 
            joints_count = self.spin.value()
            first_pos = cmds.xform(selection[0], q=True, t=True, ws=True)
            second_pos = cmds.xform(selection[1], q=True, t=True, ws=True) 
            vector = [(second_pos[0] - first_pos[0]), 
                      (second_pos[1] - first_pos[1]), 
                      (second_pos[2] - first_pos[2])]

            insert_joints = []
            for i in range(joints_count):
                insert_pos = [(first_pos[0] + vector[0] / (joints_count+1) * (i+1)),
                              (first_pos[1] + vector[1] / (joints_count+1) * (i+1)),
                              (first_pos[2] + vector[2] / (joints_count+1) * (i+1))]
                insert_joints.append(cmds.duplicate(selection[0], po=True, rc=True)[0])
                cmds.xform(insert_joints[i], t=insert_pos, ws=True) 
            
            if self.check.isChecked():
                all_joints = insert_joints
                all_joints.insert(0, selection[0])
                all_joints.append(selection[1])
                parent_world = cmds.listRelatives(selection[0], p=True)
                if parent_world == None:
                    for i in range(len(all_joints)-1):
                        cmds.parent(all_joints[i+1], all_joints[i])
                
                else:
                    parent_local = cmds.listRelatives(selection[0], p=True)[0]
                    if parent_local == selection[1]:
                        cmds.parent(selection[0], w=True)
                    
                    try:
                        for i in range(len(all_joints)-1):
                            cmds.parent(all_joints[i+1], all_joints[i])
                    
                    except:
                        cmds.undoInfo(closeChunk=True)

            else:
                cmds.parent(insert_joints, selection[0])
            
            cmds.inViewMessage(amg='<h><font color="#00FFFF">{}</hl>'.format("Created Successfully"), pos='topCenter', fade=True, a=0.2)

        else:
            cmds.inViewMessage(amg='<h><font color="#FF0000">{}</hl>'.format("Selection Error"), pos='topCenter', fade=True, a=0.2)

        cmds.undoInfo(closeChunk=True)

def main():
    global G
    try:
        G.close()
        G.deleteLater()
    except:
        pass

    G = Gui()
    G.show()

if __name__ == '__main__':
    global G
    try:
        G.close()
        G.deleteLater()
    except:
        pass
    
    G = Gui()
    G.show()