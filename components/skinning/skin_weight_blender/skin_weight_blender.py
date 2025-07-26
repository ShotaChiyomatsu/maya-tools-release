# -*- coding: utf-8 -*-

# Internal
import os
import traceback
from importlib import *
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
try:
    from PySide6 import QtWidgets, QtCore
except ImportError:
    from PySide2 import QtWidgets, QtCore

# Custom
from config import styles
reload(styles)

class Gui(MayaQWidgetBaseMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Dialog|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(os.path.splitext(os.path.basename(__file__))[0].replace('_', ' ').title().replace(' ', ''))
        self.setMinimumWidth(370)
        self.edit_mode = None
        self.ui_design()
        
    def ui_design(self):
        self.output_layout = QtWidgets.QGridLayout(self)
        self.value_box = QtWidgets.QSpinBox()
        self.value_box.setMinimum(0)
        self.value_box.setMaximum(100)
        self.value_box.setMinimumWidth(70)
        self.value_box.setSuffix("%")
        self.edit_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.edit_slider.setRange(0, 100)
        self.edit_slider.setSingleStep(10)
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.copy_button = QtWidgets.QPushButton("Copy Weight")
        self.set_button = QtWidgets.QPushButton("Set Weight")
        self.edit_button = QtWidgets.QPushButton("Edit Weight")
        self.output_layout.addWidget(self.edit_slider, 0, 0)
        self.output_layout.addWidget(self.value_box, 0, 1)
        self.output_layout.addWidget(self.reset_button, 0, 2)
        self.output_layout.addWidget(self.copy_button, 1, 0, 1, 3)
        self.output_layout.addWidget(self.set_button, 2, 0, 1, 3)
        self.output_layout.addWidget(self.edit_button, 3, 0, 1, 3)
        self.edit_slider.installEventFilter(self)
        self.edit_slider.sliderReleased.connect(self.end_chunk)
        self.edit_slider.valueChanged.connect(self.set_value_box)
        self.value_box.valueChanged.connect(self.set_value_slider)
        self.copy_button.clicked.connect(self.get_source_weight)
        self.edit_button.clicked.connect(self.get_destination_weight)
        self.set_button.clicked.connect(self.set_destination_weight)
        self.reset_button.clicked.connect(self.reset_value)
        self.value_box.valueChanged.connect(self.edit_destination_weight)
        self.setStyleSheet(styles.apply_dark_style())

    def eventFilter(self, obj, event):
        if obj == self.edit_slider and event.type() == QtCore.QEvent.MouseButtonPress:
            cmds.undoInfo(openChunk=True)
        return super(Gui, self).eventFilter(obj, event)

    def set_value_box(self):
        self.value_box.setValue(int(self.edit_slider.value()))
    
    def set_value_slider(self):
        self.edit_slider.setValue(int(self.value_box.value()))
    
    def reset_value(self):
        self.edit_mode = None
        self.edit_slider.setValue(0)
        self.edit_mode = 1
    
    def end_chunk(self):
        if self.edit_mode == None or self.edit_mode == 0:
            cmds.undoInfo(closeChunk=True)
        else:
            print("Set Weight Successfully"),
            cmds.undoInfo(closeChunk=True)
      
    def get_source_weight(self):
        try:
            self.edit_mode = 0
            if not cmds.selectPref(q=True, tso=True):
                cmds.selectPref(tso=True)   
                 
            self.source_vertex = cmds.ls(os=True, fl=True)[0]
            self.source_skin = cmds.ls(cmds.listHistory(self.source_vertex.split(".")[0]), type="skinCluster")[0]
            self.source_joints = cmds.listConnections(self.source_skin + ".matrix", s=True, t="joint")  
            for i in self.source_joints:
                cmds.setAttr(i+".liw", 0)    
            self.source_weight = cmds.skinPercent(self.source_skin, self.source_vertex, q=True, v=True)
            cmds.inViewMessage(amg='<h><font color="#00ff7f">{}</hl>'.format("Copy Weight Successfully"), 
            pos='topCenter', fade=True, a=0.2)
            
        except:
            traceback.print_exc()
            cmds.inViewMessage(amg='<h><font color="#dc143c">{}</hl>'.format("Please Select Vertex"), 
            pos='topCenter', fade=True, a=0.2)
            
    def get_destination_weight(self):
        if self.edit_mode == 0 or self.edit_mode == 1:
            if not cmds.selectPref(q=True, tso=True):
                cmds.selectPref(tso=True)  
                
            self.destination_vertex = cmds.ls(os=True, fl=True)
            self.destination_skin = cmds.ls(cmds.listHistory(self.destination_vertex[0].split(".")[0]), type="skinCluster")[0]
            if self.source_skin == self.destination_skin:
                self.edit_mode = 1
                self.destination_weight = []
                for a in range(len(self.destination_vertex)):
                    self.destination_weight.append(cmds.skinPercent(self.source_skin, self.destination_vertex[a], q=True, v=True))
                
                self.difference_weight = []
                for b in range(len(self.destination_vertex)):
                    self.difference_weight.append([])
                    for c in range(len(self.source_joints)):
                        self.difference_weight[b].append((self.source_weight[c] - self.destination_weight[b][c]) / 100)
                        
                cmds.inViewMessage(amg='<h><font color="#00ff7f">{}</hl>'.format("Enable Edit Weight"), pos='topCenter', fade=True, a=0.2)
                
            else:
                self.edit_mode = 1
                self.destination_joints = cmds.listConnections(self.destination_skin + ".matrix", s=True, t="joint")
                for i in self.destination_joints:
                    cmds.setAttr(i+".liw", 0)
                self.difference_joints = []
                for element in self.source_joints:
                    if not element in self.destination_joints:
                        self.difference_joints.append(element)
                
                if not len(self.difference_joints) == 0: 
                    cmds.inViewMessage(amg='<h><font color="#00ff7f">{}</hl>'.format("Joints requiring additional influence are now show Script Editor"),
                    pos='topCenter', fade=True, a=0.2)
                    print("{}\n>>>{}".format("Joints requiring additional influence are now show Script Editor", str(self.difference_joints))),
                
                else:
                    for element in self.destination_joints:
                        if not element in self.source_joints:
                            self.source_joints.append(element)
                            self.source_weight.append(0.0)
                    
                    order = sorted(range(len(self.destination_joints)), 
                    key=lambda k: self.source_joints.index(self.destination_joints[k]))
                    self.destination_joints = [self.destination_joints[i] for i in order]
                    
                    self.destination_weight = []
                    for a in range(len(self.destination_vertex)):
                        self.destination_weight.append([])
                        for b in range(len(self.destination_joints)):
                            self.destination_weight[a].append(cmds.skinPercent(self.destination_skin, self.destination_vertex[a], 
                            q=True, v=True, t=self.destination_joints[b]))
                    
                    self.difference_weight = []
                    for b in range(len(self.destination_vertex)):
                        self.difference_weight.append([])
                        for c in range(len(self.source_joints)):
                            self.difference_weight[b].append((self.source_weight[c] - self.destination_weight[b][c]) / 100)

                    cmds.inViewMessage(amg='<h><font color="#00ff7f">{}</hl>'.format("Enable Edit Weight"), 
                    pos='topCenter', fade=True, a=0.2)
                
        else: 
            cmds.inViewMessage(amg='<h><font color="#dc143c">{}</hl>'.format("Please Copy Weight"), 
            pos='topCenter', fade=True, a=0.2)
    
    def set_destination_weight(self):
        if self.edit_mode == 0 or self.edit_mode == 1:
            cmds.undoInfo(openChunk=True)
            self.destination_vertex = cmds.ls(os=True, fl=True)
            self.destination_skin = cmds.ls(cmds.listHistory(self.destination_vertex[0].split(".")[0]), type="skinCluster")[0]
            if self.source_skin == self.destination_skin:
                if not cmds.selectPref(q=True, tso=True):
                    cmds.selectPref(tso=True)  
                    
                self.destination_weight = []
                for a in range(len(self.destination_vertex)):
                    self.destination_weight.append(cmds.skinPercent(self.source_skin, self.destination_vertex[a], q=True, v=True))
                
                self.difference_weight = []
                for b in range(len(self.destination_vertex)):
                    self.difference_weight.append([])
                    for c in range(len(self.source_joints)):
                        self.difference_weight[b].append((self.source_weight[c] - self.destination_weight[b][c]) / 100)
                        
                self.source_joints_weights = []
                for a in range(len(self.destination_vertex)):
                    self.source_joints_weights.append([])
                    for b in range(len(self.source_joints)):
                        self.source_joints_weights[a].append([])
                        self.source_joints_weights[a][b].append(self.source_joints[b])
                        self.source_joints_weights[a][b].append((self.difference_weight[a][b] * self.edit_slider.value()) + self.destination_weight[a][b])
                for c in range(len(self.destination_vertex)):
                    cmds.skinPercent(self.source_skin, self.destination_vertex[c], tv=self.source_joints_weights[c])
                
                cmds.inViewMessage(amg='<h><font color="#00ff7f">{}</hl>'.format("Set Weight Successfully"), 
                pos='topCenter', fade=True, a=0.2)
            
            else:
                self.edit_mode = 1
                self.destination_joints = cmds.listConnections(self.destination_skin + ".matrix", s=True, t="joint")
                for i in self.destination_joints:
                    cmds.setAttr(i+".liw", 0)
                self.difference_joints = []
                for element in self.source_joints:
                    if not element in self.destination_joints:
                        self.difference_joints.append(element)
                
                if not len(self.difference_joints) == 0: 
                    cmds.inViewMessage(amg='<h><font color="#00ff7f">{}</hl>'.format("Joints requiring additional influence are now show Script Editor"),
                    pos='topCenter', fade=True, a=0.2)
                    print("{}\n>>>{}".format("Joints requiring additional influence are now show Script Editor", str(self.difference_joints))),
                
                else:
                    for element in self.destination_joints:
                        if not element in self.source_joints:
                            self.source_joints.append(element)
                            self.source_weight.append(0.0)
                    
                    order = sorted(range(len(self.destination_joints)), 
                    key=lambda k: self.source_joints.index(self.destination_joints[k]))
                    self.destination_joints = [self.destination_joints[i] for i in order]
                    
                    self.destination_weight = []
                    for a in range(len(self.destination_vertex)):
                        self.destination_weight.append([])
                        for b in range(len(self.destination_joints)):
                            self.destination_weight[a].append(cmds.skinPercent(self.destination_skin, self.destination_vertex[a], 
                            q=True, v=True, t=self.destination_joints[b]))
                    
                    self.difference_weight = []
                    for b in range(len(self.destination_vertex)):
                        self.difference_weight.append([])
                        for c in range(len(self.source_joints)):
                            self.difference_weight[b].append((self.source_weight[c] - self.destination_weight[b][c]) / 100)

                    self.source_joints_weights = []
                    for a in range(len(self.destination_vertex)):
                        self.source_joints_weights.append([])
                        for b in range(len(self.source_joints)):
                            self.source_joints_weights[a].append([])
                            self.source_joints_weights[a][b].append(self.source_joints[b])
                            self.source_joints_weights[a][b].append((self.difference_weight[a][b] * self.edit_slider.value()) + self.destination_weight[a][b])
                    for c in range(len(self.destination_vertex)):
                        cmds.skinPercent(self.destination_skin, self.destination_vertex[c], tv=self.source_joints_weights[c])
                        
                    cmds.inViewMessage(amg='<h><font color="#00ff7f">{}</hl>'.format("Set Weight Successfully"), 
                    pos='topCenter', fade=True, a=0.2)
            
            cmds.undoInfo(closeChunk=True)
        else:
            cmds.inViewMessage(amg='<h><font color="#dc143c">{}</hl>'.format("Please Copy Weight"), 
            pos='topCenter', fade=True, a=0.2)
        
    def edit_destination_weight(self):
        if self.edit_mode == 1:
            self.source_joints_weights = []
            for a in range(len(self.destination_vertex)):
                self.source_joints_weights.append([])
                for b in range(len(self.source_joints)):
                    self.source_joints_weights[a].append([])
                    self.source_joints_weights[a][b].append(self.source_joints[b])
                    self.source_joints_weights[a][b].append((self.difference_weight[a][b] * self.edit_slider.value()) + self.destination_weight[a][b])
            
            if self.source_skin == cmds.ls(cmds.listHistory(self.destination_vertex[0].split(".")[0]), type="skinCluster")[0]:
                for c in range(len(self.destination_vertex)):
                    cmds.skinPercent(self.source_skin, self.destination_vertex[c], tv=self.source_joints_weights[c])
            else:
                for c in range(len(self.destination_vertex)):
                    cmds.skinPercent(self.destination_skin, self.destination_vertex[c], tv=self.source_joints_weights[c])         
        else:
            pass
        
def main():
    global g
    try:
        g.close()
        g.deleteLater()
    except:
        pass

    g = Gui()
    g.show()

if __name__ == '__main__':
    global g
    try:
        g.close()
        g.deleteLater()
    except:
        pass
    
    g = Gui()
    g.show()