# -*- coding: utf-8 -*-
import maya.cmds as cmds

def copy_skincluster():
    selection = cmds.ls(sl=True)
    if not selection or len(selection) < 2:
        cmds.warning("メッシュを2つ以上選択してください。")
        return

    source_mesh = selection[0]

    try:
        history = cmds.listHistory(source_mesh) or []
        skin_clusters = cmds.ls(history, type="skinCluster") or []
        if not skin_clusters:
            cmds.warning("ソースメッシュにスキンクラスターが見つかりません。")
            return
        source_skincluster = skin_clusters[0]
    except Exception as e:
        cmds.warning("スキンクラスターの取得中にエラーが発生しました: %s" % e)
        return

    joints = cmds.listConnections(source_skincluster, s=True, t="joint") or []
    if not joints:
        cmds.warning("ソーススキンクラスターに接続されたジョイントが見つかりません。")
        return

    dest_meshes = selection[1:]
    for mesh in dest_meshes:
        try:
            dest_skincluster = cmds.skinCluster(mesh, joints, toSelectedBones=True, 
                                                bindMethod=0, skinMethod=0, normalizeWeights=1)[0]
            cmds.copySkinWeights(ss=source_skincluster, ds=dest_skincluster,
                                 nm=True, sm=False, sa='closestPoint',
                                 ia=('label','closestJoint','closestBone'))
            print("// Result: 正常に処理が完了しました。")
        except Exception as e:
            cmds.warning("メッシュ '%s' へのスキンコピーに失敗しました: %s" % (mesh, e))

def main():
    copy_skincluster()