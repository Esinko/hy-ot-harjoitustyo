from PySide6 import QtWidgets, QtGui, QtCore
from map.abstract import Element
from typing import List, Literal, Union
from map.types import MapText
from ui.components.editor_object import EditorObject
from ui.components.editor_properties import element
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

class AddTextEvent:
    x: int
    y: int

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y

class MoveTextEvent:
    id: int
    x: int
    y: int

    def __init__(self, id, x, y):
        self.x = x
        self.y = y
        self.id = id

class RenderingException(Exception):
    def __init__(self, object):
        super().__init__(f"Failed to render object: {object.to_dict()}")


class TileWidget(EditorObject):  # MARK: Tile
    highlight: QtWidgets.QGraphicsRectItem | None = None
    def __init__(self, *args, tile_id: int, background_image: bytes | None, rotation: int):
        super().__init__(*args, object_id=tile_id, type="element")

        # Render background or default color
        if background_image:
            # Create pixmap from image
            background = QtGui.QImage.fromData(background_image)
            pixmap = QtGui.QPixmap.fromImage(background)

            # Scale the pixmap
            scaled_pixmap = pixmap.scaled(self.rect().size().toSize())

            # Add rotation
            pixmap_center = scaled_pixmap.rect().center()
            pixmap_transform = QtGui.QTransform()
            pixmap_transform.translate(pixmap_center.x(), pixmap_center.y())
            pixmap_transform.rotate(rotation)
            pixmap_transform.translate(-pixmap_center.x(), -pixmap_center.y())
            rotated_pixmap = scaled_pixmap.transformed(pixmap_transform)

            # Paint the background
            self.setBrush(QtGui.QBrush(rotated_pixmap))
        else:
            self.setBrush(QtGui.QBrush(QtGui.QColor("#8F9092")))

    # Paint the tile and add outline when focused
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        if self.hasFocus() and not self.highlight:
            # Add outline when focused
            self.setZValue(100)
            pen = QtGui.QPen(QtGui.QColor("#F89B2E"), 2)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())


class TextWidget(EditorObject):  # MARK: Text
    text_label: GraphicsLabel
    text: MapText

    def __init__(self, *args, text: MapText, rotation: int):
        super().__init__(*args, object_id=text.id, type="text")
        self.setZValue(2)
        self.text = text

        # Create text element as label
        text_font = QtGui.QFont()
        text_font.setPointSize(text.font_size)
        self.text_label = GraphicsLabel(
            text=text.value, font=text_font, color=text.color, backgroundColor="transparent")
        self.text_label.setZValue(80)
        self.text_label.document().adjustSize()
        self.text_label.setPos(text.x, text.y)
        self.text_label.setTransformOriginPoint(self.text_label.boundingRect().center())
        self.text_label.setRotation(text.rotation)
        self.text_label.setParentItem(self)
        
        # Properly scale element based on text size
        current_rect = self.rect()
        text_rect = self.text_label.boundingRect()
        self.setRect(current_rect.x(), current_rect.y(), text_rect.width(), text_rect.height())
        

    # Paint the tile and add outline when focused
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        # Create text border
        pen = QtGui.QPen(QtGui.QColor("#000"), 2, QtCore.Qt.DashLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect())

        if self.hasFocus():
            # Add outline when focused
            self.setZValue(100)
            pen = QtGui.QPen(QtGui.QColor("#F89B2E"), 2)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())

ObjectsList = List[Union[Element, MapText]]

# NOTE: We need this here to avoid a circular dependency for now. Move to own file later.
class FocusEvent:
    id: int | None
    type = Literal["element", "text", None]

    def __init__(self, id: int, type: Literal["element", "text"]):
        self.id = id
        self.type = type

class EditorGraphicsView(QtWidgets.QGraphicsView):  # MARK: Editor
    addElementEvent = QtCore.Signal(AddElementEvent)
    moveElementEvent = QtCore.Signal(MoveElementEvent)
    addTextEvent = QtCore.Signal(AddTextEvent)
    moveTextEvent = QtCore.Signal(MoveTextEvent)
    focusObjectEvent = QtCore.Signal(FocusEvent)
    objects: ObjectsList = []
    objectWidgets: List[Union[TileWidget, TextWidget]] = []
    focusedObjectWidget: TileWidget | TextWidget | None = None
    focusedObject: MapText | Element | None = None

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

    # Remove focus with ESC
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            self._setFocusedObjectWidget(None)
            self.render(self.objects)
        else:
            super().keyPressEvent(event)

    # Things to handle on each render that are not default QT drawing stuff
    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        # Make sure correct tile has focus
        if self.focusedObject and not self.focusedObjectWidget.hasFocus():
            QtCore.QTimer.singleShot(
                0, lambda: self.focusedObjectWidget.setFocus(QtCore.Qt.OtherFocusReason))

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
        if event.mimeData().hasText() and event.mimeData().text().startswith("BDM; "):
            event.setDropAction(QtCore.Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(
        self, event: QtGui.QDragEnterEvent): self._canDrag(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent): self._canDrag(event)

    # MARK: Drag Event
    # Triggered when user has picked the location
    def dropEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasText():
            event_mime_text = event.mimeData().text()
            event.setDropAction(QtCore.Qt.DropAction.CopyAction)
            pos = event.position().toPoint()
            scene_pos = self.mapToScene(pos)

            if event_mime_text == "BDM; new_element":
                tile_x = int(scene_pos.x() //
                             self.element_size)
                tile_y = int(scene_pos.y() //
                             self.element_size)
                self.addElementEvent.emit(AddElementEvent(tile_x, tile_y, 1, 1))
                event.accept()
            elif event_mime_text.startswith("BDM; move_element "):
                target_tile = int(event_mime_text.split(" ")[2])
                tile_x = int(scene_pos.x() //
                             self.element_size)
                tile_y = int(scene_pos.y() //
                             self.element_size)
                self.moveElementEvent.emit(MoveElementEvent(target_tile, tile_x, tile_y))
                event.accept()
            elif event_mime_text.startswith("BDM; move_text "):
                target_text = int(event_mime_text.split(" ")[2])

                # Offset point to text center
                text_widget: TextWidget | None = list(filter(lambda obj: obj.id == target_text and obj.type == "text", self.objectWidgets))[0]
                if not text_widget:
                    raise RenderingException("ERROR: Unable to resolve widget for text to be moved!")
                
                text_rect = text_widget.rect()
                centered_x = scene_pos.x() - text_rect.width() / 2
                centered_y = scene_pos.y() - text_rect.height() / 2

                self.moveTextEvent.emit(MoveTextEvent(target_text, centered_x, centered_y))
                event.accept()
            elif event_mime_text == "BDM; new_text":
                self.addTextEvent.emit(AddTextEvent(scene_pos.x(), scene_pos.y(), 1, 1))
                event.accept()
            else:
                event.setDropAction(QtCore.Qt.DropAction.IgnoreAction)
                print(f"WARNING: Unsupported drag event, tried: {event_mime_text}")
        else:
            event.ignore()
            print("WARNING: Drag event did not contain data. Ignored.")

    # MARK: Set focus
    # Set focused object in the editor
    def _setFocusedObjectWidget(self, object: TileWidget | TextWidget | None):
        if object == None:
            self.focusedObject = None
            self.focusedObjectWidget = None
            self.focusObjectEvent.emit(FocusEvent(None, None))
        else:
            self.focusedObjectWidget = object
            self.focusedObject = list(filter(lambda obj: obj.id == object.id and obj.type == object.type, self.objects))[0]
            if not self.focusedObject:
                raise RenderingException("ERROR: Object to focus is not in objects cache! Cannot focus.")
            self.focusObjectEvent.emit(FocusEvent(object.id, object.type))
        self.viewport().update()

    # Add grid elements to the map
    # MARK: Render

    def _render_element_object(self, element: Element) -> bool:
        # Create tile
        tile = TileWidget(element.x * self.element_size, # x
                          element.y * self.element_size, # y
                          self.element_size, # w
                          self.element_size, # h
                          tile_id=element.id,
                          background_image=element.background_image.data if element.background_image != None else None,
                          rotation=element.rotation)

        tile.focusEvent.connect(lambda: self._setFocusedObjectWidget(tile))
        self.scene().addItem(tile)
        self.objectWidgets.append(tile)

        # Update in focus tile
        gave_focus = False
        if self.focusedObject != None and element.id == self.focusedObject.id and self.focusedObject.type == "element":
            gave_focus = True
            self._setFocusedObjectWidget(tile)

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

        return gave_focus

    def _render_text_object(self, text: MapText) -> bool:
        # Create text widget
        text_widget = TextWidget(text.x, # x
                                 text.y, # y
                                 1,
                                 1,
                                 text=text,
                                 rotation=text.rotation)

        text_widget.focusEvent.connect(lambda: self._setFocusedObjectWidget(text_widget))
        self.scene().addItem(text_widget)
        self.objectWidgets.append(text_widget)

        # Update in focus text
        gave_focus = False
        if self.focusedObject != None and text.id == self.focusedObject.id and self.focusedObject.type == "text":
            gave_focus = True
            self._setFocusedObjectWidget(text_widget)

        # Handle focus
        text_widget.focusEvent.connect(lambda: self._setFocusedObjectWidget(text_widget))
        return gave_focus

    def render(self, objects: ObjectsList) -> None:
        # Clear the scene and canvas
        self.scene().clear()
        self.objects = objects
        self.objectWidgets = []
        gave_focus = False
        
        # Render all objects
        for object in objects:
            if object.type == "element":
                did_focus = self._render_element_object(object)
                if did_focus:
                    gave_focus = True
            elif object.type == "text":
                did_focus = self._render_text_object(object)
                if did_focus:
                    gave_focus = True
            else:
                raise RenderingException(object)

        # If nothing gained focus, clear it
        if not gave_focus:
            self._setFocusedObjectWidget(None)
