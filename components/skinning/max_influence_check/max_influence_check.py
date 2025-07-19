# -*- coding: utf-8 -*-
import os
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from PySide6 import QtWidgets, QtCore

class Gui(MayaQWidgetBaseMixin, QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Dialog|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(os.path.splitext(os.path.basename(__file__))[0].replace('_', ' ').title().replace(' ', ''))
        self.ui_design()
    
    def ui_design(self):
        outputLayout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel("Max Influences :")
        self.spinBox = QtWidgets.QSpinBox()
        self.spinBox.setMinimum(1)
        self.button = QtWidgets.QPushButton("Apply")
        outputLayout.addWidget(self.label)
        outputLayout.addWidget(self.spinBox)
        outputLayout.addWidget(self.button)
        self.button.clicked.connect(lambda:check_max_influence(self.spinBox.value()))  
        self.setStyleSheet("font-weight:bold") 

def check_max_influence(max_influence):
    exceeding_vertices = []
    cmds.select(clear=True)
    try:
        skin_clusters = cmds.ls(type="skinCluster") or []
    except Exception as e:
        cmds.warning("スキンクラスターの取得に失敗しました: %s" % e)
        return

    for skin_cluster in skin_clusters:
        try:
            meshes = cmds.skinCluster(skin_cluster, q=True, geometry=True) or []
        except Exception as e:
            cmds.warning("スキンクラスターの取得に失敗しました: %s" % (e))
            continue

        for mesh in meshes:
            verts = check_mesh_influence(max_influence, skin_cluster, mesh)
            exceeding_vertices.extend(verts)

    if exceeding_vertices:
        msg = "最大インフルエンス数 %s を超えている頂点が %s 個あります。" % (max_influence, len(exceeding_vertices))
        print(msg)
        cmds.inViewMessage(amg='<hl>%s</hl>' % msg, pos='topCenter', fade=True, alpha=.9)
        cmds.select(exceeding_vertices)
    else:
        msg = "最大インフルエンス数 %s を超える頂点はありませんでした。" % max_influence
        print(msg)
        cmds.inViewMessage(amg=msg, pos='topCenter', fade=True, alpha=.9)

def check_mesh_influence(max_influence, cluster, mesh):
    exceeding = []
    try:
        vertices = cmds.polyListComponentConversion(mesh, toVertex=True)
        if not vertices:
            return exceeding
        vertices = cmds.filterExpand(vertices, selectionMask=31) or []
    except Exception as e:
        cmds.warning("メッシュ '%s' の頂点情報の取得に失敗しました: %s" % (mesh, e))
        return exceeding

    for vert in vertices:
        try:
            joints = cmds.skinPercent(cluster, vert, query=True, ignoreBelow=0.000001, transform=None) or []
        except Exception as e:
            cmds.warning("頂点 '%s' のウェイト情報の取得に失敗しました: %s" % (vert, e))
            continue

        if len(joints) > max_influence:
            exceeding.append(vert)

    if exceeding:
        print("%s に最大インフルエンス数を超える頂点があります: %s 個" % (mesh, len(exceeding)))

    return exceeding

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