# -*- coding: utf-8 -*-
import maya.cmds as cmds
from PySide2.QtWidgets import * 
from PySide2.QtGui import *
from PySide2.QtCore import * 
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance
from maya import OpenMayaUI

try:
    G.close()
except:
    pass

def baseWindow():
    mainWindow = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindow), QWidget)

class Gui(QDialog):
    
    def __init__(self, parent=baseWindow()):
        super(Gui, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog|Qt.WindowCloseButtonHint)
        self.setWindowTitle("InsertJointsBetween")
        self.UiDesign()
    
    def UiDesign(self):
        outputLayout = QHBoxLayout(self)
        self.label = QLabel("Joints :")
        self.check = QCheckBox("Chain")
        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMinimumWidth(40)
        self.spin.setMaximumWidth(40)
        self.button = QPushButton("Insert")
        self.button.setMinimumWidth(100)
        self.button.setMaximumWidth(100)
        outputLayout.addWidget(self.label)
        outputLayout.addWidget(self.spin)
        outputLayout.addWidget(self.check)
        outputLayout.addWidget(self.button)
        self.setStyleSheet("font-weight:bold;")
        self.button.clicked.connect(self.InsertJointsBetween)  

    def InsertJointsBetween(self):
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

G = 0
def main():
    global G
    G = Gui()
    G.show()

if __name__ == '__main__':
    G = Gui()
    G.show()