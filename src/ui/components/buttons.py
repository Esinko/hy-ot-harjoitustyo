from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtSvgWidgets import QSvgWidget  # This is required because QT
from os.path import abspath


class AddObjectButtonWidget(QtWidgets.QPushButton):
    """Special styled button for adding an object to the editor.
    """
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

        # Use given icon as preview
        pixmap = QtGui.QPixmap(self.size())
        pixmap.fill(QtGui.QColor("#8F9092"))
        icon_pixmap = self.icon().pixmap(self.iconSize())
        painter = QtGui.QPainter(pixmap)
        icon_rect = QtCore.QRect(
            (pixmap.width() - icon_pixmap.width()) // 2,
            (pixmap.height() - icon_pixmap.height()) // 2,
            icon_pixmap.width(),
            icon_pixmap.height()
        )
        painter.drawPixmap(icon_rect, icon_pixmap)
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(QtCore.QPoint(16, 16))
        drag.exec(QtCore.Qt.DropAction.CopyAction)


class AddElementButtonWidget(AddObjectButtonWidget):
    """Add an element to the editor button with drag support.
    """

    def __init__(self, parent=None):
        super().__init__(QtGui.QIcon(abspath("./ui/icons/add-tile.svg")),
                         "BDM; new_element", parent)


class AddTextButtonWidget(AddObjectButtonWidget):
    """Add an element to the editor button with drag support.
    """

    def __init__(self, parent=None):
        super().__init__(QtGui.QIcon(abspath("./ui/icons/add-text.svg")), "BDM; new_text", parent)


class IconButtonWidget(QtWidgets.QPushButton):
    """Generic style button with only an icon.
    """

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
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #535353, stop:1 #646464);
            }
        """)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))


class DeleteButtonWidget(IconButtonWidget):
    """Icon button with a trash icon.
    """

    def __init__(self, box_size: int = 32, parent=None):
        super().__init__(parent=parent)
        icon = QtGui.QIcon(abspath("./ui/icons/trash.svg"))
        self.setIcon(icon)
        if box_size < 9:
            box_size = 9
        self.setIconSize(QtCore.QSize(box_size - 8, box_size - 8))
        self.setFixedSize(box_size, box_size)


class RenameButtonWidget(IconButtonWidget):
    """Icon button with a pencil icon.
    """

    def __init__(self, box_size: int = 32, parent=None):
        super().__init__(parent=parent)
        icon = QtGui.QIcon(abspath("./ui/icons/edit.svg"))
        self.setIcon(icon)
        if box_size < 9:
            box_size = 9
        self.setIconSize(QtCore.QSize(box_size - 8, box_size - 8))
        self.setFixedSize(box_size, box_size)


class SelectPathEvent:
    path: Path

    def __init__(self, selected_path):
        # TODO: Handle read issue here?
        self.path = Path(selected_path)


class ExportMapButton(IconButtonWidget):
    """Icon button with a share icon which opens a dialog to pick a location for a map.
    """
    # TODO: Convert to group, add filename in read-only text line, then add X and select buttons on the right
    selectPathEvent = QtCore.Signal(SelectPathEvent)
    placeholder_name: str

    def _select_file(self):
        selected_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Select Location",
            abspath("./untitled.dmap")
            if not self.placeholder_name else
            abspath(f"./{self.placeholder_name}"),
            "Maps (*.dmap)"
        )
        self.selectPathEvent.emit(SelectPathEvent(selected_path))

    def __init__(self, box_size: int = 32, parent=None, placeholder_name=""):
        super().__init__(parent=parent)
        icon = QtGui.QIcon(abspath("./ui/icons/share.svg"))
        self.setIcon(icon)
        self.placeholder_name = placeholder_name
        if box_size < 9:
            box_size = 9
        self.setIconSize(QtCore.QSize(box_size - 8, box_size - 8))
        self.setFixedSize(box_size, box_size)
        self.clicked.connect(self._select_file)


class StandardButtonWidget(QtWidgets.QPushButton):
    """Basic styled button with an optional icon.
    """
    text: str = ""

    def __init__(self, text: str, icon: QtGui.QIcon = None, parent=None):
        super().__init__(parent=parent)
        self.text = text
        self.setStyleSheet("""
            QPushButton {
                color: white;
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #373737, stop:1 #535353);
                border: 1px solid #292929;
                border-radius: 4px;
                padding: 4px 8px;
                text-align: left;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #FDA239, stop:1 #F0851B);
            }
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #535353, stop:1 #646464);
            }
        """)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        if icon:
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(16, 16))
            self.setText(f"  {text}")
        else:
            self.setText(text)

# Copy, to avoid a circular import
# TODO: Create a dedicated "events" file?


class SelectFileEvent:
    file: Path
    name: str
    data: bytes

    def __init__(self, file_path):
        # TODO: Handle read issue here?
        self.file = Path(file_path)
        self.data = self.file.read_bytes()
        self.name = self.file.name


class ImportMapButton(StandardButtonWidget):
    """An icon button which allows the user to pick a map file to import. 

    Args:
        StandardButtonWidget (_type_): _description_
    """
    # TODO: Convert to group, add filename in read-only text line, then add X and select buttons on the right
    selectFileEvent = QtCore.Signal(SelectFileEvent)

    def _select_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select Map",
            "",
            "Maps (*.dmap)"
        )
        if file_path:
            self.selectFileEvent.emit(SelectFileEvent(file_path))

    def __init__(self, parent=None):
        super().__init__(text="Import Map", parent=parent)
        self.clicked.connect(self._select_file)
