# -*- coding: utf-8 -*-

# Internal
import maya.cmds as cmds

def main():
    joints = get_joints()
    if joints:
        mesh_name = input_mesh_name()
        if mesh_name:
            positions = get_world_positions(joints)
            mesh = create_faces_from_positions(positions, mesh_name)
            check_and_reverse_normals(mesh)

def get_joints():
    root_joints = cmds.ls(sl=True, type="joint")
    if len(root_joints) < 2:
        cmds.inViewMessage(amg='<h><font color="#FF0000">{}</hl>.'.format("最低でも２つ以上のルートジョイントを選択した状態で実行してください"), 
                           pos='topCenter', 
                           fade=True, 
                           a=0.2) 
                           
        return False

    else:
        all_joints = []
        for root_joint in root_joints:
            cmds.select(root_joint, hi=True)
            all_joints.append(cmds.ls(sl=True, type="joint"))
        
        tree_joints = []
        for i in range(len(all_joints[0])):
            tree_joints.append([])
            for j in range(len(all_joints)):
                tree_joints[i].append(all_joints[j][i])
    
        return tree_joints

def input_mesh_name():
    result = cmds.promptDialog(
        title='JointToMeshCreator',
        message='Mesh Name:',
        button=['Apply', 'Cancel'],
        defaultButton='Apply',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    
    if result == 'Apply':
        input_text = cmds.promptDialog(query=True, text=True)
        return input_text
    else:
        cmds.inViewMessage(amg='<h><font color="#00ff7f">{}</hl>.'.format("JointToMeshCreatorはキャンセルされました"), 
                           pos='topCenter', 
                           fade=True, 
                           a=0.2) 
        return False

def get_world_positions(joint_list):
    positions = []
    for row in joint_list:
        row_positions = []
        for jnt in row:
            if cmds.objExists(jnt):
                pos = cmds.xform(jnt, q=True, ws=True, t=True)
                row_positions.append(pos)

        positions.append(row_positions)
        
    return positions

def create_faces_from_positions(positions, mesh_name):
    all_faces = []
    for row_index in range(len(positions) - 1):
        row1 = positions[row_index]
        row2 = positions[row_index + 1]
        for i in range(len(row1)):
            p1 = row1[i]
            p2 = row2[i]
            p3 = row2[(i + 1) % len(row2)]
            p4 = row1[(i + 1) % len(row1)]
            face = cmds.polyCreateFacet(p=[p1, p2, p3, p4], ch=False)[0]
            all_faces.append(face)

    if all_faces:
        combined_mesh = cmds.polyUnite(all_faces, ch=False, mergeUVSets=True)[0]
        cmds.polyMergeVertex(combined_mesh, d=0.001) 
        cmds.delete(combined_mesh, ch=True)
        mesh = cmds.rename(combined_mesh, mesh_name)
    
    return mesh

def check_and_reverse_normals(mesh):
    vertices = cmds.ls(f"{mesh}.vtx[*]", flatten=True)
    center = cmds.objectCenter(mesh, gl=True) 
    reversed_normals = False
    for vertex in vertices:
        position = cmds.pointPosition(vertex, world=True)
        normal = cmds.polyNormalPerVertex(vertex, query=True, xyz=True)
        to_vertex = [position[0] - center[0], position[1] - center[1], position[2] - center[2]]
        dot_product = sum(n * t for n, t in zip(normal, to_vertex))
        if dot_product < 0:
            reversed_normals = True
            break
    
    cmds.select(mesh)
    cmds.inViewMessage(amg='<h><font color="#00FFFF">Created Successfully!!!</hl>.', pos='topCenter', fade=True, a=0.2)