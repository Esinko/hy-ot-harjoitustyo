from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtSvgWidgets import QSvgWidget  # This is required because QT
from os.path import abspath


class AddObjectButtonWidget(QtWidgets.QPushButton):
    mime_text: str = ""

    def __init__(self, icon: QtGui.QIcon, mime_text: str, parent=None):
        super().__init__(parent=parent)
        self.mime_text = mime_text
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(24, 24))
        self.setFixedSize(32, 32)
        self.setStyleSheet("""
            QPushButton {
                color: white;
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #373737, stop:1 #535353);
                border: 1px solid #292929;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.DragCopyCursor))
        self.pressed.connect(self.start_drag)

    def start_drag(self):
        # TODO: Update preview
        drag = QtGui.QDrag(self)
        mime = QtCore.QMimeData()
        mime.setText(self.mime_text)
        drag.setMimeData(mime)

        # New element preview
        # TODO: Add type based preview
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtGui.QColor("#8F9092"))
        drag.setPixmap(pixmap)
        drag.setHotSpot(QtCore.QPoint(16, 16))

        drag.exec(QtCore.Qt.DropAction.CopyAction)


class AddElementButtonWidget(AddObjectButtonWidget):
    def __init__(self, parent=None):
        super().__init__(QtGui.QIcon(abspath("./ui/icons/add-tile.svg")),
                         "BDM; new_element", parent)


class AddTextButtonWidget(AddObjectButtonWidget):
    def __init__(self, parent=None):
        super().__init__(QtGui.QIcon(abspath("./ui/icons/add-text.svg")), "BDM; new_text", parent)


class IconButtonWidget(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("""
            QPushButton {
                color: white;
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #373737, stop:1 #535353);
                border: 1px solid #292929;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #FDA239, stop:1 #F0851B);
            }
        """)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))


class DeleteButtonWidget(IconButtonWidget):
    def __init__(self, box_size: int = 32, parent=None):
        super().__init__(parent=parent)
        icon = QtGui.QIcon(abspath("./ui/icons/trash.svg"))
        self.setIcon(icon)
        if box_size < 9:
            box_size = 9
        self.setIconSize(QtCore.QSize(box_size - 8, box_size - 8))
        self.setFixedSize(box_size, box_size)


class RenameButtonWidget(IconButtonWidget):
    def __init__(self, box_size: int = 32, parent=None):
        super().__init__(parent=parent)
        icon = QtGui.QIcon(abspath("./ui/icons/edit.svg"))
        self.setIcon(icon)
        if box_size < 9:
            box_size = 9
        self.setIconSize(QtCore.QSize(box_size - 8, box_size - 8))
        self.setFixedSize(box_size, box_size)


class StandardButtonWidget(QtWidgets.QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("""
            QPushButton {
                color: white;
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #373737, stop:1 #535353);
                border: 1px solid #292929;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #FDA239, stop:1 #F0851B);
            }
        """)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setText(text)
