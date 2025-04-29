from PySide6 import QtWidgets, QtCore


class EditorSidebar(QtWidgets.QWidget):
    """Styled base widget for the editor sidebar.
    """
    sidebar_layout: QtWidgets.QVBoxLayout

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("editorSidebar")
        self.setFixedWidth(260)
        self.setStyleSheet("""
            #editorSidebar {
                background-color: #727272;
                border-left: 1px solid black;              
            }
        """)
        self.sidebar_layout = QtWidgets.QVBoxLayout(self)
        self.sidebar_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.sidebar_layout.setSpacing(0)
        self.setLayout(self.sidebar_layout)
