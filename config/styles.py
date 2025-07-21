# -*- coding: utf-8 -*-

def apply_dark_style():
    dark_style = """
    QWidget {
        background-color: #2e2e2e;
        color: #f0f0f0;
        font-family: 'Segoe UI', 'Meiryo', sans-serif;
        font-size: 10pt;
    }

    QGroupBox {
        background-color: #3a3a3a;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        margin-top: 20px;
        padding: 0px;
    }

    QGroupBox:title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 0px;
        background-color: transparent;
        color: #f0f0f0;
    }

    QLabel {
        background-color: transparent;
        padding: 2px;
    }  

    QCheckBox {
        background-color: transparent;
        color: #f0f0f0;
    }

    QCheckBox::indicator:unchecked{
        background : transparent;
        border : 1px solid #000000;
        border-radius : 2px;
    }

    QSpinBox {
        border-radius: 4px;
        padding: 2px;
        background-color: #525252;
        border: 1px solid #2e2e2e;
    } 

    QLineEdit {
        border-radius: 4px;
        padding: 2px;
        background-color: #525252;
        border: 1px solid #525252;
    } 

    QPushButton {
        background-color: #525252;
        border: 1px solid #525252;
        color: #ffffff;
        border-radius: 4px;
        padding: 2px;
    }

    QPushButton:hover {
        background-color: #5a5a5a;
    }

    QPushButton:pressed {
        background-color: #2d2d2d;
    }

    QSlider::groove:horizontal {
        border: 1px solid #444444;
        height: 8px;
        background: #525252;
        margin: 2px 0;
        border-radius: 4px;
    }

    QSlider::handle:horizontal {
        background: #888888;
        border: 1px solid transparent;
        width: 14px;
        height: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }

    """

    return dark_style