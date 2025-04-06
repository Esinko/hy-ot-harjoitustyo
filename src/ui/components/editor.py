from PySide6 import QtWidgets, QtGui, QtCore
from map.abstract import Element
from typing import List
from ui.components.typography import GraphicsLabel


class AddElementEvent:
    x: int
    y: int
    width: int
    height: int

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class MoveElementEvent:
    id: int
    x: int
    y: int

    def __init__(self, id, x, y):
        self.x = x
        self.y = y
        self.id = id


class FocusElementEvent:
    id: int

    def __init__(self, id):
        self.id = id

# MARK: Tile


class TileWidget(QtCore.QObject, QtWidgets.QGraphicsRectItem):
    focusEvent = QtCore.Signal(FocusElementEvent)
    id: int
    edit_circle_radius = 32

    def __init__(self, *args, id: int,  **kwargs):
        QtCore.QObject.__init__(self)
        QtWidgets.QGraphicsRectItem.__init__(self, *args, **kwargs)
        self.id = id
        self.setBrush(QtGui.QBrush(QtGui.QColor("#8F9092")))
        self.setAcceptedMouseButtons(
            QtCore.Qt.MouseButton.LeftButton | QtCore.Qt.MouseButton.RightButton)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setZValue(1)

    # Paint the tile and add outline when focused
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.hasFocus():
            # Add outline
            self.setZValue(100)  # So outline is on top of other tiles
            pen = QtGui.QPen(QtGui.QColor("#F89B2E"), 2)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())

            # Draw draggable circle in center
            center = self.rect().center()
            fill = QtGui.QColor("#FFFFFF")
            fill.setAlpha(184)
            painter.setBrush(QtGui.QBrush(fill))
            painter.setPen(QtGui.QPen(QtGui.QColor("white"), 4))
            painter.drawEllipse(
                center, self.edit_circle_radius, self.edit_circle_radius)
        else:
            self.setZValue(1)

    # Only allow right mouse button to set focus
    def focusInEvent(self, event: QtGui.QFocusEvent):
        if QtWidgets.QApplication.mouseButtons() != QtCore.Qt.MouseButton.RightButton and event.reason() != QtCore.Qt.FocusReason.OtherFocusReason:
            self.clearFocus()
            event.ignore()
            return
        self.focusEvent.emit(FocusElementEvent(self.id))
        super().focusInEvent(event)

    # Only remove focus if clicked somewhere else
    def focusOutEvent(self, event: QtGui.QFocusEvent):
        # Ignore losing focus if it's not to another TileWidget
        if isinstance(QtWidgets.QApplication.focusWidget(), TileWidget):
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
                mime.setText(f"BDM; move_tile {self.id}")
                drag.setMimeData(mime)
                # TODO: Update preview
                pixmap = QtGui.QPixmap(32, 32)
                pixmap.fill(QtGui.QColor("#8F9092"))
                drag.setPixmap(pixmap)
                drag.setHotSpot(QtCore.QPoint(16, 16))
                drag.exec(QtCore.Qt.DropAction.CopyAction)

                # Restore drag mode
                view.setDragMode(
                    QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
                event.accept()
                return
        super().mousePressEvent(event)

# MARK: Editor


class EditorGraphicsView(QtWidgets.QGraphicsView):
    addElementEvent = QtCore.Signal(AddElementEvent)
    moveElementEvent = QtCore.Signal(MoveElementEvent)
    elements: List[Element] = []
    tileWidgets: List[TileWidget] = []
    focusedTileWidget: TileWidget | None = None
    focusedTileId: int | None = None

    def __init__(self, is_preview: bool = False):
        super().__init__()

        # Styling & QT configs
        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setAcceptDrops(True)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#393939")))
        # Large space for "infinite" area
        self.setSceneRect(-10000, -10000, 20000, 20000)
        if not is_preview:
            self.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setTransformationAnchor(
                QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Configuration
        self.element_size = 256
        self.scale_factor = 0.3
        self.min_scale = 0.01
        self.max_scale = 5.0
        self.scale(self.scale_factor, self.scale_factor)

        # Coordinate label
        self.coord_label = QtWidgets.QLabel("x: 0, y: 0", self)
        self.coord_label.setStyleSheet(
            "color: white; background: rgba(0,0,0,0.5); padding: 2px; font-size: 12px;")
        self.coord_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)

    # Get the adjusted coordinates
    def _getAdjustedCoordinate(self, coordinate: int | float):
        return coordinate // self.element_size

    # Handle manipulating the map position
    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        coord_text = f"x: {self._getAdjustedCoordinate(int(scene_pos.x()))}, y: {self._getAdjustedCoordinate(int(scene_pos.y()))}"
        self.coord_label.setText(coord_text)
        self.coord_label.setFixedWidth(len(coord_text) * 6)
        super().mouseMoveEvent(event)

    # Make sure coordinate label is in the right place
    def resizeEvent(self, event):
        self.coord_label.move(5, self.viewport().height() -
                              self.coord_label.height() - 5)
        self.coord_label.resize(self.viewport().width(), 20)
        super().resizeEvent(event)

    # Handle manipulating the map zoom
    def wheelEvent(self, event: QtGui.QWheelEvent):
        delta = event.angleDelta().y()
        zoom_in = delta > 0
        factor = 1.1 if zoom_in else 0.9
        new_scale = self.scale_factor * factor

        # Clamp zoom
        if new_scale < self.min_scale or new_scale > self.max_scale:
            return

        self.scale(factor, factor)
        self.scale_factor = new_scale

    # Things to handle on each render that are not default QT drawing stuff
    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        # Make sure correct tile has focus
        if self.focusedTileWidget and not self.focusedTileWidget.hasFocus():
            QtCore.QTimer.singleShot(
                0, lambda: self.focusedTileWidget.setFocus(QtCore.Qt.OtherFocusReason))

        super().drawForeground(painter, rect)

    # Draw the editor background
    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawBackground(painter, rect)

        left = int(rect.left()) - (int(rect.left()) % self.element_size)
        top = int(rect.top()) - (int(rect.top()) % self.element_size)

        pen = QtGui.QPen(QtGui.QColor(80, 80, 80))  # dark gray
        pen.setStyle(QtCore.Qt.PenStyle.DashLine)
        painter.setPen(pen)

        x = left
        while x < rect.right():
            painter.drawLine(QtCore.QPointF(x, rect.top()),
                             QtCore.QPointF(x, rect.bottom()))
            x += self.element_size

        y = top
        while y < rect.bottom():
            painter.drawLine(QtCore.QPointF(rect.left(), y),
                             QtCore.QPointF(rect.right(), y))
            y += self.element_size

    # Handle dropped elements
    def _canDrag(self, event: QtGui.QDragEnterEvent | QtGui.QDragMoveEvent):
        if event.mimeData().hasText() and event.mimeData().text().startswith("BDM; "):  # Accept only add tiles for now
            event.setDropAction(QtCore.Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(
        self, event: QtGui.QDragEnterEvent): self._canDrag(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent): self._canDrag(event)

    # Triggered when user has picked the location
    def dropEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasText():
            if event.mimeData().text() == "BDM; new_tile":
                event.setDropAction(QtCore.Qt.DropAction.CopyAction)
                pos = event.position().toPoint()
                scene_pos = self.mapToScene(pos)
                self.addElementEvent.emit(AddElementEvent(int(scene_pos.x(
                ) // self.element_size), int(scene_pos.y() // self.element_size), 1, 1))
                event.accept()
            elif event.mimeData().text().startswith("BDM; move_tile "):
                target_tile = int(event.mimeData().text().split(" ")[2])
                event.setDropAction(QtCore.Qt.DropAction.CopyAction)
                pos = event.position().toPoint()
                scene_pos = self.mapToScene(pos)
                self.moveElementEvent.emit(MoveElementEvent(target_tile, int(
                    scene_pos.x() // self.element_size), int(scene_pos.y() // self.element_size)))
                event.accept()
        else:
            event.ignore()

    # Set focused tile in the editor
    def _setFocusedTile(self, tile: TileWidget):
        self.focusedTileWidget = tile
        self.focusedTileId = tile.id
        self.viewport().update()

    # Add grid elements to the map
    def render(self, elements: List[Element]):
        self.scene().clear()
        self.elements = elements
        self.tileWidgets = []

        for element in elements:
            # Create tile
            tile = TileWidget(element.x * self.element_size, element.y *
                              self.element_size, self.element_size, self.element_size, id=element.id)
            # The parameter magic here forces python to use the tile from this iteration of the loop!
            tile.focusEvent.connect(lambda _, t=tile: self._setFocusedTile(t))
            self.scene().addItem(tile)
            self.tileWidgets.append(tile)

            # Update in focus tile
            if element.id == self.focusedTileId:
                self._setFocusedTile(tile)

            # Create tile name
            label = GraphicsLabel(
                text=element.name, backgroundColor="#000", color="white")
            label.setParentItem(tile)
            label.setPos(
                (element.x * self.element_size) + 10,
                (element.y * self.element_size) + 10
            )

            # Create tile position
            label = GraphicsLabel(
                text=f"x: {element.x}, y: {element.y}", backgroundColor="#000", color="white")
            label.setParentItem(tile)
            label_rect = label.boundingRect()
            label.setPos(
                (element.x * self.element_size) +
                self.element_size - label_rect.width() - 10,
                (element.y * self.element_size) +
                self.element_size - label_rect.height() - 10
            )
