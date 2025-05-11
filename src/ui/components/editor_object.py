from os.path import abspath
from typing import Literal
from PySide6 import QtWidgets, QtGui, QtCore


class FocusEvent:
    id: int | None
    type = Literal["element", "text", None]

    def __init__(self, id: int, type: Literal["element", "text"]):
        self.id = id
        self.type = type


class EditorObject(QtCore.QObject, QtWidgets.QGraphicsRectItem):
    """Class to inherit for widgets to render in the editor graphics view. Especially important for focus handling.

    Attributes:
        focusEvent (QSignal): Signal when an object wants to gain focus.
        type (str): Object type (often element or text)
        id (int): Unique id usually from the DB
        edit_circle_radius (32): Hardcoded edit circle size
    """
    focusEvent = QtCore.Signal(FocusEvent)
    type: str = "any"
    id: int
    edit_circle_radius: int = 32

    def __init__(self, *args, object_id: int, type: str, **kwargs):
        QtCore.QObject.__init__(self)
        QtWidgets.QGraphicsRectItem.__init__(self, *args, **kwargs)
        self.id = object_id
        self.type = type

        self.setPen(QtCore.Qt.NoPen)

        # Mouse config and zValue
        self.setAcceptedMouseButtons(
            QtCore.Qt.MouseButton.LeftButton | QtCore.Qt.MouseButton.RightButton)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setZValue(1)

    # Paint the tile and add outline when focused
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        self.setZValue(1)

        if self.hasFocus():
            # Draw draggable circle in center
            center = self.rect().center()
            fill = QtGui.QColor("#FFFFFF")
            fill.setAlpha(184)
            painter.setBrush(QtGui.QBrush(fill))
            painter.setPen(QtGui.QPen(QtGui.QColor("white"), 4))
            painter.drawEllipse(
                center, self.edit_circle_radius, self.edit_circle_radius)
            
            # Add outline
            self.setZValue(100)
            pen = QtGui.QPen(QtGui.QColor("#F89B2E"), 2)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())

    # Only allow right mouse button to set focus
    def focusInEvent(self, event: QtGui.QFocusEvent):
        if QtWidgets.QApplication.mouseButtons() != QtCore.Qt.MouseButton.RightButton and event.reason() != QtCore.Qt.FocusReason.OtherFocusReason:
            self.clearFocus()
            event.ignore()
            return
        self.focusEvent.emit(FocusEvent(self.id, self.type))
        super().focusInEvent(event)

    # Only remove focus if clicked somewhere else
    def focusOutEvent(self, event: QtGui.QFocusEvent):
        # Ignore losing focus if it's not to another object
        if isinstance(QtWidgets.QApplication.focusWidget(), EditorObject):
            super().focusOutEvent(event)
        else:
            event.ignore()

    # Handle dragging to other position
    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        if self.hasFocus() and event.button() == QtCore.Qt.MouseButton.LeftButton:
            center = self.rect().center()
            dist = (event.pos() - center).manhattanLength()

            # Check if we clicked inside the circle
            if dist <= self.edit_circle_radius:
                # Disable view dragging
                view = self.scene().views()[0]
                view.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)

                drag = QtGui.QDrag(self)
                mime = QtCore.QMimeData()
                mime.setText(f"BDM; move_{self.type} {self.id}")
                drag.setMimeData(mime)

                icon = QtGui.QIcon(abspath("./ui/icons/move.svg"))
                size = icon.actualSize(QtCore.QSize(32, 32))
                pixmap = QtGui.QPixmap(size)
                pixmap.fill(QtGui.QColor("#8F9092"))
                icon_pixmap = icon.pixmap(size)
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

                # Restore drag mode
                view.setDragMode(
                    QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
                event.accept()
                return
        
        super().mousePressEvent(event)
