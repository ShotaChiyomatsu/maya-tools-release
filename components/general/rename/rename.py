import re
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from PySide6 import QtWidgets, QtCore

class Gui(MayaQWidgetBaseMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Rename")
        self.ui_design()

    def ui_design(self):
        output_layout = QtWidgets.QVBoxLayout(self)
        self.number_check = QtWidgets.QCheckBox("Number")
        self.count_start = QtWidgets.QSpinBox()
        self.count_start.setMinimum(1)
        self.count_start.setPrefix("0")
        self.branch_button = QtWidgets.QPushButton("Branch")
        group_setting = QtWidgets.QGroupBox("Setting")
        layout_setting = QtWidgets.QGridLayout()
        layout_setting.addWidget(self.number_check, 0, 0)
        layout_setting.addWidget(self.count_start, 0, 1)
        layout_setting.addWidget(self.branch_button, 0, 2)
        group_setting.setLayout(layout_setting)
        group_setting.setStyleSheet("font-weight:bold")
        group_setting.setMaximumHeight(55)

        group_edit = QtWidgets.QGroupBox("Edit")
        layout_edit = QtWidgets.QGridLayout()
        label_texts = ["Name", "Prefix", "Suffix", "Search", "Replace"]
        self.name_edit, self.prefix_edit, self.suffix_edit, self.search_edit, self.replace_edit = [QtWidgets.QLineEdit() for _ in label_texts]
        for i, text in enumerate(label_texts):
            layout_edit.addWidget(QtWidgets.QLabel(text), i, 0)
            layout_edit.addWidget([self.name_edit, self.prefix_edit, self.suffix_edit, self.search_edit, self.replace_edit][i], i, 1)

        group_edit.setLayout(layout_edit)
        group_edit.setStyleSheet("font-weight:bold")

        output_layout.addWidget(group_setting)
        output_layout.addWidget(group_edit)

        self.branch_button.clicked.connect(self.branch_select)
        self.name_edit.returnPressed.connect(self.name_set)
        self.prefix_edit.returnPressed.connect(self.prefix_set)
        self.suffix_edit.returnPressed.connect(self.suffix_set)
        self.replace_edit.returnPressed.connect(self.replace_set)

    def branch_select(self):
        cmds.undoInfo(openChunk=True)
        cmds.select(hi=True)
        cmds.undoInfo(closeChunk=True)

    def name_set(self):
        cmds.undoInfo(openChunk=True)
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            cmds.warning("何も選択されていません")
            cmds.undoInfo(closeChunk=True)
            return

        if self.number_check.isChecked():
            count = self.count_start.value()
            for i in range(len(selection)):
                current_selection = cmds.ls(sl=True, long=True)
                new_name = "%s%02d" % (self.name_edit.text(), count)
                cmds.rename(current_selection[i], new_name)
                count += 1
        else:
            for i in range(len(selection)):
                current_selection = cmds.ls(sl=True, long=True)
                new_name = self.name_edit.text()
                cmds.rename(current_selection[i], new_name)

        cmds.undoInfo(closeChunk=True)

    def prefix_set(self):
        cmds.undoInfo(openChunk=True)
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            cmds.warning("何も選択されていません")
            cmds.undoInfo(closeChunk=True)
            return

        if self.number_check.isChecked():
            count = self.count_start.value()
            for i in range(len(selection)):
                current_selection = cmds.ls(sl=True, long=True)
                base_name = selection[i].split("|")[-1]
                new_name = "%s%s%02d" % (self.prefix_edit.text(), base_name, count)
                cmds.rename(current_selection[i], new_name)
                count += 1
        else:
            for i in range(len(selection)):
                current_selection = cmds.ls(sl=True, long=True)
                base_name = selection[i].split("|")[-1]
                new_name = "%s%s" % (self.prefix_edit.text(), base_name)
                cmds.rename(current_selection[i], new_name)

        cmds.undoInfo(closeChunk=True)

    def suffix_set(self):
        cmds.undoInfo(openChunk=True)
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            cmds.warning("何も選択されていません")
            cmds.undoInfo(closeChunk=True)
            return

        if self.number_check.isChecked():
            count = self.count_start.value()
            for i in range(len(selection)):
                current_selection = cmds.ls(sl=True, long=True)
                base_name = selection[i].split("|")[-1]
                new_name = "%s%s%02d" % (base_name, self.suffix_edit.text(), count)
                cmds.rename(current_selection[i], new_name)
                count += 1
        else:
            for i in range(len(selection)):
                current_selection = cmds.ls(sl=True, long=True)
                base_name = selection[i].split("|")[-1]
                new_name = "%s%s" % (base_name, self.suffix_edit.text())
                cmds.rename(current_selection[i], new_name)

        cmds.undoInfo(closeChunk=True)

    def replace_set(self):
        cmds.undoInfo(openChunk=True)
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            cmds.warning("何も選択されていません")
            cmds.undoInfo(closeChunk=True)
            return
        
        search_text = self.search_edit.text()
        replace_text = self.replace_edit.text()

        if self.number_check.isChecked():
            count = self.count_start.value()
            for i in range(len(selection)):
                current_selection = cmds.ls(sl=True, long=True)
                base_name = selection[i].split("|")[-1]
                new_name = "%s%02d" % (base_name.replace(search_text, replace_text), count)
                cmds.rename(current_selection[i], new_name)
                count += 1
        else:
            for i in range(len(selection)):
                current_selection = cmds.ls(sl=True, long=True)
                base_name = selection[i].split("|")[-1]
                new_name = base_name.replace(search_text, replace_text)
                cmds.rename(current_selection[i], new_name)

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