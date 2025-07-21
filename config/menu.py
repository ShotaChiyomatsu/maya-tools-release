# -*- coding: utf-8 -*-
import os
from maya import cmds

def main():
    # Maya上部にメニューバーを追加
    menu_name = "ChiyoTools"
    cmds.menu(label=menu_name, parent="MayaWindow", tearOff=True)

    # 設定に必要なディレクトリを取得
    config_path = os.path.dirname(os.path.abspath(__file__))
    menu_Path = config_path.replace("config", "")
    components_path = menu_Path + "components\\"

    # 構成要素を取得
    components = [d for d in os.listdir(components_path) if os.path.isdir(os.path.join(components_path, d))] 

    # generalがリストの先頭に来るように変更
    components.remove("general")
    components.insert(0, "general")

    # ラベルを追加
    cmds.menuItem(divider=True, dividerLabel="Tools")

    # 構成要素をメニューバーに追加
    for component in components:
        cmds.menuItem(label=component.capitalize(), image="%s\icons\%s.png" % (config_path, component), tearOff=True, subMenu=True)
        # 構成要素ごとにツールを追加
        tool_path = components_path + component
        tools = [d for d in os.listdir(tool_path) if os.path.isdir(os.path.join(tool_path, d))] 
        for tool in tools:
            command = "from importlib import *\nimport components.%s.%s.%s as %s\nreload(%s)\n%s.main()" % ((component,) + (tool,) * 5)
            help_command = "import webbrowser\nwebbrowser.open('https://github.com/ShotaChiyomatsu/maya-tools-release', new=2, autoraise=True)"
            cmds.menuItem(label=tool.replace('_', ' ').title().replace(' ', ''), command=command)
            cmds.menuItem(optionBox=True, optionBoxIcon="%s\icons\help.png" % (config_path), command=help_command)
        
        cmds.setParent("..", menu=True)

    # ドキュメントを追加
    cmds.menuItem(divider=True, dividerLabel="Help")
    cmds.menuItem(label="Document", image="%s\icons\info.png" % (config_path),
    command="import webbrowser\nwebbrowser.open('https://github.com/ShotaChiyomatsu/maya-tools-release', new=2, autoraise=True)")