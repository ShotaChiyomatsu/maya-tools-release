# -*- coding: utf-8 -*-

# Internal
import os
from importlib import *
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
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
        self.ui_design()
    
    def ui_design(self):
        output_layout = QtWidgets.QGridLayout(self)
        self.radio_01 = QtWidgets.QRadioButton("All Scene Mesh")
        self.radio_02 = QtWidgets.QRadioButton("Selected Mesh")
        self.radio_02.setChecked(True)
        self.label = QtWidgets.QLabel("MaxInfluences")
        self.spinBox = QtWidgets.QSpinBox()
        self.spinBox.setMinimum(1)
        self.spinBox.setValue(4)
        self.button = QtWidgets.QPushButton("Apply")
        output_layout.addWidget(self.radio_01, 0, 0, 1, 3)
        output_layout.addWidget(self.radio_02, 0, 3, 1, 3)
        output_layout.addWidget(self.label, 1, 0, 1, 2)
        output_layout.addWidget(self.spinBox, 1, 2, 1, 2)
        output_layout.addWidget(self.button, 1, 4, 1, 2)
        self.setStyleSheet(styles.apply_dark_style())
        self.button.clicked.connect(lambda:self.edit_round_weights(self.spinBox.value()))

    def find_meshes_with_high_influence(self, max_influence):
        meshes = []
        skin_clusters = []
        if self.radio_01.isChecked() == True:
            all_meshes = cmds.ls(type="mesh", long=True)
        else:
            selection = cmds.ls(selection=True, long=True)
            all_meshes = []
            for element in selection:
                all_meshes.append(cmds.listRelatives(element, children=True, fullPath=True, type="mesh")[0])

        transforms = list(set(cmds.listRelatives(all_meshes, parent=True, fullPath=True) or []))
        for mesh in transforms:
            history = cmds.listHistory(mesh)
            skin_cluster = None
            for node in history:
                if cmds.nodeType(node) == "skinCluster":
                    skin_cluster = node
                    break

            if not skin_cluster:
                continue

            vtx_count = cmds.polyEvaluate(mesh, vertex=True)
            for i in range(vtx_count):
                influences = cmds.skinPercent(skin_cluster, "%s.vtx[%d]" % (mesh, i), query=True, transform=None)
                if len(influences) > max_influence:
                    meshes.append(mesh)
                    skin_clusters.append(skin_cluster)
                    break

        meshes = list(set(meshes))
        return meshes, skin_clusters

    def get_round_weights(self, weights, max_influence):
        indexed_weights = list(enumerate(weights))
        sorted_weights = sorted(indexed_weights, key=lambda x: x[1], reverse=True)
        kept = sorted_weights[:max_influence]
        removed = sorted_weights[max_influence:]
        removed_total = sum(w for _, w in removed)
        kept_total = sum(w for _, w in kept)
        redistributed = [
            (i, w + (w / kept_total) * removed_total)
            for i, w in kept
        ]
        result_weights = [0.0] * len(weights)
        for i, w in redistributed:
            result_weights[i] = w

        return result_weights

    def edit_round_weights(self, max_influence):
        cmds.undoInfo(openChunk=True)
        meshes, skin_clusters = self.find_meshes_with_high_influence(max_influence)
        for mesh, skin_cluster in zip(meshes, skin_clusters):
            # 頂点数を取得
            vtx_count = cmds.polyEvaluate(mesh, vertex=True)
            # ジョイントを取得
            joints = cmds.listConnections(skin_cluster + ".matrix", s=True, t="joint")
            # ウェイト値を取得
            selection_list = OpenMaya.MSelectionList()
            selection_list.add(mesh)
            mesh_obj, mesh_comp = selection_list.getComponent(0)
            selection_list = OpenMaya.MSelectionList()
            selection_list.add(skin_cluster)
            skin_obj = selection_list.getDependNode(0)
            skin_cluster_obj = OpenMayaAnim.MFnSkinCluster(skin_obj)
            weights, inf_count = skin_cluster_obj.getWeights(mesh_obj, mesh_comp)
            weights_flat = list(weights)
            vertex_count = len(weights_flat) // inf_count
            weights = [weights_flat[i * inf_count:(i + 1) * inf_count] for i in range(vertex_count)]
            # ポストに変更
            cmds.skinCluster(skin_cluster, e=True, nw=2)
            # ジョイントのロックを解除
            for joint in joints:
                cmds.setAttr("%s.liw" % (joint), 0) 
            # ウェイト値を編集
            for i in range(vtx_count):
                if sum(1 for w in weights[i] if w >= 0.000001) >= max_influence:
                    result_weights = self.get_round_weights(weights[i], max_influence)
                    tv_values = list(zip(joints, result_weights))
                    cmds.skinPercent(skin_cluster, "%s.vtx[%d]" % (mesh, i), tv=tv_values)
            # インタラクティブに変更
            cmds.skinCluster(skin_cluster, e=True, nw=1)
            # 終了時のメッセージを表示
            cmds.select(None)
            cmds.inViewMessage(amg='<h><font color="#5AFF19">MaxInfluenceの最適化が正常に完了しました</hl>',
            pos='topCenter', fade=True, a=0.2)
            cmds.undoInfo(closeChunk=True)

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