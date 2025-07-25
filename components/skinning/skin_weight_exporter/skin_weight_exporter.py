# -*- coding: utf-8 -*-

# Internal
import os
import json
import traceback
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
                    cmds.progressBar(self.help_line, edit=True, step=1)
                # データを作成
                data = {
                    "Type":object_type,
                    "Joints":joints,
                    "Weights":weights,
                    "Vertex_Number":vertex_number
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
            vertex_count = sum([cmds.polyEvaluate(cmds.listRelatives(selection[i], s=True)[0], v=True) for i in range(len(selection))])
            cmds.progressBar(self.help_line, e=True, bp=True, status="Export...", min=0, max=vertex_count, ii=False)
            object_type = "Mesh"
            for element in selection:
                # スキンクラスターを取得
                skin_cluster = cmds.ls(cmds.listHistory(element), type="skinCluster")
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

                data = {
                    "Type":object_type,
                    "Joints":joints,
                    "Weights":weights
                    }
                
                # ファイルに書き込み
                with open("%s\\%s.json" % (self.line_edit.text(), element), "w") as f:
                    json.dump(data, f, indent=4)

                # 終了時のメッセージを表示
                cmds.progressBar(self.help_line, edit=True, endProgress=True)
                cmds.inViewMessage(amg='<h><font color="#5AFF19">ウェイト値のエクスポートが完了しました!!</hl>',
                pos='topCenter', fade=True, a=0.2)


        
        


    """
    def weightExport(self):
        cmds.undoInfo(openChunk=True)
        file_path = "{}{}\\Documents\\maya\\projects\\default".format(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"))
        try:
            os.makedirs("{}\\json".format(file_path))
        except:
            pass
        
        selection = cmds.ls(sl=True, fl=True)
        if cmds.objectType(selection[0]) == "transform":
            # �i���󋵂�\��
            all_vertex = [cmds.polyEvaluate(cmds.listRelatives(selection[i], s=True)[0], v=True) for i in range(len(selection))]
            all_vertices = sum(all_vertex)
            progressBar = cmds.progressBar(self.helpLine, edit=True, beginProgress=True, status="Export...", 
            minValue=0, maxValue=all_vertices, isInterruptable=False)
            
            skinCluster = []
            vertex = []
            joints = []
            weights = []
            joints_weights = []
            weights_map = []
            joints_weights_map = []
            weight_file = []
            vtx_joints_weight = {}
            for a in range(len(selection)):
                # SkinCluster���擾
                skinCluster.append(cmds.ls(cmds.listHistory(selection[a]), type="skinCluster")[0]) 
                # �o�C���h����Ă���W���C���g���擾
                joints.append(cmds.listConnections(skinCluster[0]+".matrix", s=True, t="joint"))
                # ���b�V���̒��_�����擾
                vertex.append(cmds.polyEvaluate(selection[a], v=True))
                # �E�F�C�g�l�𐳋K��
                for c in range(len(joints[0])):
                    cmds.setAttr(joints[0][c]+".liw", 0)
                cmds.skinPercent(skinCluster[0], nrm=True)
                # �W���C���g�ƃE�F�C�g�l�����X�g�Ŏ擾
                for d in range(vertex[0]):
                    joints_weights.append([])
                    weights.append(cmds.skinPercent(skinCluster[0], (selection[a] + ".vtx[" + str(d) + "]"), q=True, v=True))
                    for e in range(len(joints[0])):
                        joints_weights[d].append([])
                        joints_weights[d][e].append(joints[0][e])
                        joints_weights[d][e].append(weights[d][e])
            
                    # ���_�ƃW���C���g�ƃE�F�C�g�l�������^�Ŏ擾
                    vtx_joints_weight.setdefault(str(d)+"_wt", joints_weights[d])
                    vtx_joints_weight.setdefault(str(d)+"_pos", cmds.xform("{}.vtx[{}]".format(selection[a], str(d)), q=True, t=True))
                    cmds.progressBar(progressBar, edit=True, step=1)
                    
                # Json�t�@�C���ɏ����o��
                vtx_joints_weight.setdefault("type", "transform")
                vtx_joints_weight.setdefault("skinCluster", skinCluster[0])
                vtx_joints_weight.setdefault("vertex", vertex[0])
                vtx_joints_weight.setdefault("joints", joints[0])
                weight_file.append(open("{}\\json\\{}.json".format(file_path, selection[a]),'w'))
                json.dump(vtx_joints_weight, weight_file[0])
                # ���X�g����ɂ��� 
                del skinCluster[:]
                del vertex[:]
                del joints[:]
                del weights[:]
                del joints_weights[:]
                del weight_file[:]
                vtx_joints_weight.clear()
                
            cmds.progressBar(progressBar, edit=True, endProgress=True)
            print("Export Successfully!!!>>>{}\\json".format(file_path)),
            cmds.undoInfo(closeChunk=True)
            
        elif cmds.objectType(selection[0]) == "mesh":
            selected_vertex = cmds.ls(sl=True, fl=True)
            progressBar = cmds.progressBar(self.helpLine, edit=True, beginProgress=True, status="Export...", 
            minValue=0, maxValue=len(selected_vertex), isInterruptable=False)
            skinCluster = cmds.ls(cmds.listHistory(selected_vertex[0].split(".")[0]), type="skinCluster")[0]
            joints = cmds.listConnections(skinCluster+".matrix", s=True, t="joint")
            weights = []
            joints_weights = []
            item = {}
            # �W���C���g�ƃE�F�C�g�l�����X�g�Ŏ擾
            for a in range(len(selected_vertex)):
                joints_weights.append([])
                weights.append(cmds.skinPercent(skinCluster, selected_vertex[a], q=True, v=True))
                for b in range(len(joints)):
                    joints_weights[a].append([])
                    joints_weights[a][b].append(joints[b])
                    joints_weights[a][b].append(weights[a][b])
                
                cmds.progressBar(progressBar, edit=True, step=1)
            
            item.setdefault("type", "mesh")
            item.setdefault("skinCluster", skinCluster)
            item.setdefault("vertex", selected_vertex)
            item.setdefault("weight", joints_weights)
            weight_file = open("{}\\json\\{}.json".format(file_path, selected_vertex[0].split(".")[0]),'w')
            json.dump(item, weight_file)
            cmds.progressBar(progressBar, edit=True, endProgress=True)
            print("Export Successfully!!!>>>{}\\json".format(file_path)),
            cmds.undoInfo(closeChunk=True)
        
        else:
            pass

    def weightImport(self):
        cmds.undoInfo(openChunk=True)
        file_path = "{}{}\\Documents\\maya\\projects\\default".format(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"))
        selection = cmds.ls(sl=True)
        # �i���󋵂�\��
        all_vertex = [cmds.polyEvaluate(cmds.listRelatives(selection[i], s=True)[0], v=True) for i in range(len(selection))]
        all_vertices = sum(all_vertex)
        progressBar = cmds.progressBar(self.helpLine, edit=True, beginProgress=True, status="Import...", 
        minValue=0, maxValue=all_vertices, isInterruptable=False)
        weight_file = []
        item_dict = []
        for a in range(len(selection)):
            # Json�t�@�C�������[�h
            weight_file.append(open("{}\\json\\{}.json".format(file_path, selection[a]),'r'))
            item_dict.append(json.load(weight_file[0]))
            if item_dict[0]["type"] == "transform":
                # ���b�V���ƃW���C���g���o�C���h
                cmds.skinCluster(item_dict[0]["joints"], selection[a], n=item_dict[0]["skinCluster"], tsb=True)
                # ���_�ԍ��œ]��
                if self.vertexNumberButton.isChecked() == True:
                    for b in range(item_dict[0]["vertex"]):
                        cmds.skinPercent(item_dict[0]["skinCluster"], "{}.vtx[{}]".format(selection[a], str(b)), 
                        tv=item_dict[0][str(b)+"_wt"])
                        cmds.progressBar(progressBar, edit=True, step=1)
                # �ŋߐڒ��_�œ]��   
                elif self.closestVertexButton.isChecked() == True:
                    count = []
                    vertexNum = []
                    in_pos = []
                    vertexList = [i for i in range(cmds.polyEvaluate(cmds.listRelatives(selection[a], s=True)[0], v=True))] 
                    for b in range(len(vertexList)):
                        in_pos.append(cmds.xform("{}.vtx[{}]".format(selection[a], str(b)), q=True, t=True))
                        closest_vtx_pos = None
                        temp_length = None
                        for c in range(item_dict[0]["vertex"]):  
                            temp_pos = om2.MPoint(item_dict[0][str(c)+"_pos"])
                            delta = (temp_pos - om2.MPoint(in_pos[b])).length()
                            if temp_length is None or delta < temp_length:
                                count.append(c)
                                closest_vtx_pos = temp_pos
                                temp_length = delta
             
                        vertexNum.append(count[-1:][0])
                        cmds.skinPercent(item_dict[0]["skinCluster"], "{}.vtx[{}]".format(selection[a], str(b)), 
                        tv=item_dict[0][str(vertexNum[b])+"_wt"])
                        cmds.progressBar(progressBar, edit=True, step=1)
                        del count[:]
                    
                # UV�œ]�� 
                else:
                    cmds.skinCluster(cmds.listRelatives(selection[a], s=True)[0], e=True, ub=True)
                    print("This is a feature that has not been implemented"),
            
            elif item_dict[0]["type"] == "mesh":
                if self.vertexNumberButton.isChecked() == True:
                    for b in range(len(item_dict[0]["vertex"])):
                        cmds.skinPercent(item_dict[0]["skinCluster"], item_dict[0]["vertex"][b], tv=item_dict[0]["weight"][b])
                
                elif self.closestVertexButton.isChecked() == True:
                    print("This is a feature that has not been implemented"),
                
                else:
                    print("This is a feature that has not been implemented"),
            
            del weight_file[:]
            del item_dict[:]
            
        cmds.progressBar(progressBar, edit=True, endProgress=True)
        print("Import Successfully!!!"),
        cmds.undoInfo(closeChunk=True)
            
    def resetBindPose(self):
        try:
            cmds.delete(cmds.ls(type="dagPose"))
        except:
            pass
            
        cmds.select("JT_Root", hi=True)
        cmds.dagPose(cmds.ls(sl=True, type="joint"), s=True, bp=True)
        cmds.select(None)
        print("Reset Successfully!!!"),
    
    """

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