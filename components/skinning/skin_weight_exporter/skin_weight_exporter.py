# -*- coding: utf-8 -*-

# Internal
import os
import json
from importlib import *
from maya import cmds, mel
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from maya.api import OpenMaya
from maya.api import OpenMayaAnim
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
        self.setMinimumWidth(320)
        self.help_line = mel.eval("$tmp = $gMainProgressBar")
        self.ui_design()
        
    def ui_design(self):
        self.output_layout = QtWidgets.QGridLayout(self)
        self.line_edit = QtWidgets.QLineEdit(os.path.dirname(__file__)+"\\temp")
        self.line_edit.setReadOnly(True)
        self.open_button = QtWidgets.QPushButton("Open")
        self.export_button = QtWidgets.QPushButton("Export Weight")
        self.import_button = QtWidgets.QPushButton("Import Weight")
        self.separator = QtWidgets.QFrame()
        self.separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.output_layout.addWidget(self.line_edit, 0, 0, 1, 3)
        self.output_layout.addWidget(self.open_button, 0, 3, 1, 1)
        self.output_layout.addWidget(self.separator, 1, 0, 1, 4)
        self.output_layout.addWidget(self.export_button, 2, 0, 1, 4)
        self.output_layout.addWidget(self.import_button, 3, 0, 1, 4)
        self.open_button.clicked.connect(lambda:self.open_folder(self.line_edit.text()))
        self.export_button.clicked.connect(self.create_temp_folder)
        self.export_button.clicked.connect(self.weight_export)
        self.import_button.clicked.connect(self.weight_import)
        self.setStyleSheet(styles.apply_dark_style())
    
    def open_folder(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            # ファルダを開く
            os.startfile(path)
        else:
            cmds.inViewMessage(amg='<h><font color="#FFFF66">フォルダが存在しません：{}</hl>'.format(path), pos='topCenter', fade=True, a=0.2)

    def create_temp_folder(self):
        # フォルダを作成
        temp_path = self.line_edit.text()
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
    
    def weight_export(self):
        selection = cmds.ls(sl=True, fl=True)
        if ".vtx[" in selection[0]:
            vertex_count = len(selection)
            cmds.progressBar(self.help_line, e=True, bp=True, status="Export...", min=0, max=vertex_count, ii=False)
            object_type = "Vertex"
            mesh = selection[0].split(".")[0]
            # スキンクラスターを取得
            skin_cluster = cmds.ls(cmds.listHistory(mesh), type="skinCluster")
            if skin_cluster:
                # スキンウェイトを正規化
                cmds.skinPercent(skin_cluster[0], nrm=True)
                # ジョイントを取得
                joints = cmds.listConnections(skin_cluster[0] + ".matrix", s=True, t="joint")
                # ウェイト値を取得
                weights = []
                vertex_number = []
                for element in selection:  
                    weights.append(cmds.skinPercent(skin_cluster[0], element, q=True, v=True))
                    vertex_number.append(element.split(".")[-1])
                    # プログレスバーを進める
                    cmds.progressBar(self.help_line, edit=True, step=1)
                # データを作成
                data = {
                    "Type":object_type,
                    "Joints":joints,
                    "Weights":weights,
                    "VertexNumber":vertex_number
                    }
                # ファイルに書き込み
                with open("%s\\%s.json" % (self.line_edit.text(), mesh), "w") as f:
                    json.dump(data, f, indent=4)
                # 終了時のメッセージを表示
                cmds.progressBar(self.help_line, edit=True, endProgress=True)
                cmds.inViewMessage(amg='<h><font color="#5AFF19">ウェイト値のエクスポートが完了しました!!</hl>',
                pos='topCenter', fade=True, a=0.2)
            else:
                # エラー時のメッセージを表示
                cmds.inViewMessage(amg='<h><font color="#FFFF66">スキンクラスターが存在しません：{}</hl>'.format(mesh), 
                pos='topCenter', fade=True, a=0.2)
        else:
            # プログレスバーを表示
            mesh_count = len(selection)
            cmds.progressBar(self.help_line, e=True, bp=True, status="Export...", min=0, max=mesh_count, ii=False)
            object_type = "Mesh"
            for element in selection:
                # スキンクラスターを取得
                skin_cluster = cmds.ls(cmds.listHistory(element), type="skinCluster")
                if skin_cluster:
                    # スキンウェイトを正規化
                    cmds.skinPercent(skin_cluster[0], nrm=True)
                    # ジョイントを取得
                    joints = cmds.listConnections(skin_cluster[0] + ".matrix", s=True, t="joint")
                    # ウェイト値を取得
                    selection_list = OpenMaya.MSelectionList()
                    selection_list.add(element)
                    mesh_obj, mesh_comp = selection_list.getComponent(0)
                    selection_list = OpenMaya.MSelectionList()
                    selection_list.add(skin_cluster[0])
                    skin_obj = selection_list.getDependNode(0)
                    skin_cluster = OpenMayaAnim.MFnSkinCluster(skin_obj)
                    weights, inf_count = skin_cluster.getWeights(mesh_obj, mesh_comp)
                    weights_flat = list(weights)
                    vertex_count = len(weights_flat) // inf_count
                    weights = [weights_flat[i * inf_count:(i + 1) * inf_count] for i in range(vertex_count)]
                    # データを作成
                    data = {
                        "Type":object_type,
                        "Joints":joints,
                        "Weights":weights
                        }
                    # ファイルに書き込み
                    with open("%s\\%s.json" % (self.line_edit.text(), element), "w") as f:
                        json.dump(data, f, indent=4)
                    # プログレスバーを進める
                    cmds.progressBar(self.help_line, edit=True, step=1)
                    print("ウェイト値のエクスポートが完了しました：%s" % (element))
                else:
                    # エラー時のメッセージを表示
                    print("スキンクラスターが存在しません：%s" % (element))
                    
            # 終了時のメッセージを表示
            cmds.progressBar(self.help_line, edit=True, endProgress=True)
            cmds.inViewMessage(amg='<h><font color="#5AFF19">ウェイト値のエクスポートが完了しました!!</hl>',
            pos='topCenter', fade=True, a=0.2)
    
    def weight_import(self):
        cmds.undoInfo(openChunk=True)
        selection = cmds.ls(sl=True)
        # ファイルが存在しているか確認
        json_path_list = []
        selection_list = []
        vtx_count = 0
        for element in selection:
            json_path = "%s\\%s.json" % (self.line_edit.text(), element)
            if os.path.exists(json_path):
                json_path_list.append(json_path)
                selection_list.append(element)
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    weights = data["Weights"]
                    vtx_count += len(weights)
            else:
                # エラー時のメッセージを表示
                print("ウェイト情報のファイルが存在しません：%s" % (element))
        
        # プログレスバーを表示
        cmds.progressBar(self.help_line, e=True, bp=True, status="Import...", min=0, max=vtx_count, ii=False)

        # ウェイト値をインポート
        for mesh, json_file in zip(selection_list, json_path_list):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                joints = data["Joints"]
                weights = data["Weights"]
                if data["Type"] == "Mesh":
                    skin_cluster = cmds.ls(cmds.listHistory(mesh), type="skinCluster")
                    if not skin_cluster:
                        # スキンクラスターを作成
                        skin_cluster = cmds.skinCluster(joints, mesh, n="SC_" + mesh, tsb=True)[0]
                        # ポストに変更
                        cmds.skinCluster(skin_cluster, e=True, nw=2)
                        # ウェイトを転送
                        for i in range(len(weights)):
                            tv_values = list(zip(joints, weights[i]))
                            cmds.skinPercent(skin_cluster, "%s.vtx[%d]" % (mesh, i), tv=tv_values)
                            # プログレスバーを進める
                            cmds.progressBar(self.help_line, edit=True, step=1)
                        # インタラクティブに変更
                        cmds.skinCluster(skin_cluster, e=True, nw=1)
                    else:
                        # エラー時のメッセージを表示
                        print("バインドを解除してから実行して下さい：%s" % (mesh))
                else:
                    skin_cluster = cmds.ls(cmds.listHistory(mesh), type="skinCluster")
                    if skin_cluster:
                        # 現在のジョイントの情報を取得
                        current_joints = cmds.listConnections(skin_cluster[0] + ".matrix", s=True, t="joint")
                        missing = set(current_joints) - set(joints)
                        # ジョイントの情報が一致しなければループを抜ける
                        if missing:
                            print("ジョイントの情報が一致しません：%s" % (mesh))
                            continue
                        # 頂点番号を取得
                        vertex_number = data["VertexNumber"]
                        # ポストに変更
                        cmds.skinCluster(skin_cluster[0], e=True, nw=2)
                        # ウェイトを転送
                        for i in range(len(weights)):
                            tv_values = list(zip(joints, weights[i]))
                            cmds.skinPercent(skin_cluster[0], "%s.%s" % (mesh, vertex_number[i]), tv=tv_values)
                            # プログレスバーを進める
                            cmds.progressBar(self.help_line, edit=True, step=1)
                        # インタラクティブに変更
                            cmds.skinCluster(skin_cluster[0], e=True, nw=1)
                    else:
                        # エラー時のメッセージを表示
                        print("ジョイントをメッシュにバインドしてから実行して下さい：%s" % (mesh))
            
            # プログレスバーを進める
            cmds.progressBar(self.help_line, edit=True, step=1)
        
        # 終了時のメッセージを表示
        cmds.progressBar(self.help_line, edit=True, endProgress=True)
        cmds.inViewMessage(amg='<h><font color="#5AFF19">ウェイト値のインポートが完了しました!!</hl>',
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