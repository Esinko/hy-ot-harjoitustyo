from dataclasses import dataclass
from copy import deepcopy
from PySide6 import QtWidgets, QtGui, QtCore
from map.types import Element
from typing import List, Literal, Union
from map.types import MapText
from ui.components.editor_object import EditorObject
from ui.components.typography import GraphicsLabel


@dataclass
class AddElementEvent:
    x: int
    y: int
    width: int
    height: int


@dataclass
class MoveElementEvent:  # TODO: Combine text and element add+move events?
    id: int
    x: int
    y: int


@dataclass
class AddTextEvent:
    x: int
    y: int


@dataclass
class MoveTextEvent:
    id: int
    x: int
    y: int


class RenderingException(Exception):
    """Exception raised when rendering of the editor graphics fails.
    """

    def __init__(self, object):
        """Constructor of the rendering exception.

        Args:
            object(dict): The dict form of the object that caused this error. 
        """
        super().__init__(f"Failed to render object: {object.to_dict()}")


class TileWidget(EditorObject):  # MARK: Tile
    """A single tile element on the map.
    """
    is_preview: bool

    def __init__(self, *args, tile_id: int, background_image: bytes | None = None, background_color: str | None = None, rotation: int = 0, is_preview: bool):
        """Constructor of the tile element to create a new tile to be rendered.

        Args:
            tile_id (int): The id of the element to render.
            background_image (bytes | None): The raw bytes of the element background. Defaults to None.
            rotation (int): The rotation of the element's contents. Defaults to 0.
        """
        super().__init__(*args, object_id=tile_id, type="element")
        self.is_preview = is_preview

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
            self.setBrush(QtGui.QBrush(QtGui.QColor(background_color or "#8F9092")))

    def paint(self, painter, option, widget):
        # Create tile border
        if not self.is_preview:
            pen = QtGui.QPen(QtGui.QColor("#000"), 1, QtCore.Qt.SolidLine)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())

        super().paint(painter, option, widget)


class TextWidget(EditorObject):  # MARK: Text
    """A single text object rendered on the map.

    Attributes:
        text_label (GraphicsLabel): The graphics item that handles text rendering
        text (MapText): The text form information
        is_preview (bool): Only render the contents to preview final map
    """
    text_label: GraphicsLabel
    text: MapText
    is_preview: bool

    def __init__(self, *args, text: MapText, is_preview: bool):
        super().__init__(*args, object_id=text.id, type="text")
        self.setZValue(2)
        self.text = text
        self.is_preview = is_preview

        # Create text element as label
        text_font = QtGui.QFont()
        text_font.setPointSize(text.font_size)
        self.text_label = GraphicsLabel(
            text=text.value, font=text_font, color=text.color, backgroundColor="transparent")
        self.text_label.document().adjustSize()
        self.text_label.setPos(text.x, text.y)
        self.text_label.setParentItem(self)

        # Properly scale element based on text size
        current_rect = self.rect()
        text_rect = self.text_label.boundingRect()
        self.setRect(current_rect.x(), current_rect.y(),
                     text_rect.width(), text_rect.height())

        # Add rotation
        self.setTransformOriginPoint(
            self.boundingRect().center())
        self.setRotation(text.rotation)

    def paint(self, painter, option, widget):
        # Create text border
        if not self.is_preview:
            pen = QtGui.QPen(QtGui.QColor("#000"), 2, QtCore.Qt.DashLine)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())

        super().paint(painter, option, widget)


ObjectsList = List[Union[Element, MapText]]


# NOTE: We need this here to avoid a circular dependency for now. Move to own file later.
class FocusEvent:
    id: int | None
    type = Literal["element", "text", None]

    def __init__(self, id: int, type: Literal["element", "text"]):
        self.id = id
        self.type = type


class EditorGraphicsView(QtWidgets.QGraphicsView):  # MARK: Editor
    """The editor graphics element. Renders the editor contents. This class does not support snake case.
    Contains a bunch of overrides.

    Attributes:
        addElementEvent (QSignal): Signal when an element is to be added.
        moveElementEvent (QSignal): Signal when an element is to be moved.
        addTextEvent (QSignal): Signal when text is to be added.
        moveTextEvent (QSignal): Signal when text is to be moved.
        focusObjectEvent (QSignal): Signal when a specific object gains focus.
        objects (ObjectsList): List of objects to render
        objectWidgets (List[Union[TileWidget, TextWidget]]): QT constructs used for rendering
        focusedObjectWidget (TileWidget | TextWidget | None): The current widget in focus, if something is in focus
        focusedObject (MapText | Element | None): The data of the object in focus, if something is in focus.

    Raises:
        RenderingException: For unexpected issues while rendering. Blocking.
    """
    addElementEvent = QtCore.Signal(AddElementEvent)
    moveElementEvent = QtCore.Signal(MoveElementEvent)
    addTextEvent = QtCore.Signal(AddTextEvent)
    moveTextEvent = QtCore.Signal(MoveTextEvent)
    pasteElementEvent = QtCore.Signal(Element)
    pasteTextEvent = QtCore.Signal(MapText)
    focusObjectEvent = QtCore.Signal(FocusEvent)
    removeElementEvent = QtCore.Signal(int)
    removeTextEvent = QtCore.Signal(int)
    objects: ObjectsList = []
    objectWidgets: List[Union[TileWidget, TextWidget]] = []
    focusedObjectWidget: TileWidget | TextWidget | None = None
    focusedObject: MapText | Element | None = None
    is_preview: bool
    clipboard: MapText | Element | None = None

    def __init__(self, is_preview: bool = False):
        """Constructor of the editor. Styles the graphics view and scales it.

        Args:
            is_preview (bool, optional): If this graphics view should be preview only. Defaults to False.
        """
        super().__init__()
        self.is_preview = is_preview

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
        
    def set_preview(self, is_preview: bool):
        """Set the editor preview mode

        Args:
            is_preview (bool): Enable/disable preview mode
        """
        self.is_preview = is_preview
        self.render(self.objects)

    def _getAdjustedCoordinate(self, coordinate: int | float):
        """Get the adjusted 1/256 coordinates.

        Args:
            coordinate (int | float): Coordinate to convert

        Returns:
            int: Adjusted coordinates
        """
        return coordinate // self.element_size

    def mouseMoveEvent(self, event):
        # Handle manipulating the map position
        scene_pos = self.mapToScene(event.pos())
        coord_text = f"x: {self._getAdjustedCoordinate(int(scene_pos.x()))}, y: {self._getAdjustedCoordinate(int(scene_pos.y()))}"
        self.coord_label.setText(coord_text)
        self.coord_label.setFixedWidth(len(coord_text) * 6)
        super().mouseMoveEvent(event)

    def resizeEvent(self, event):
        # Make sure coordinate label is in the right place
        self.coord_label.move(5, self.viewport().height() -
                              self.coord_label.height() - 5)
        self.coord_label.resize(self.viewport().width(), 20)
        super().resizeEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        # Handle manipulating the map zoom
        delta = event.angleDelta().y()
        zoom_in = delta > 0
        factor = 1.1 if zoom_in else 0.9
        new_scale = self.scale_factor * factor

        # Clamp zoom
        if new_scale < self.min_scale or new_scale > self.max_scale:
            return

        self.scale(factor, factor)
        self.scale_factor = new_scale

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            # Remove focus with ESC
            self._setFocusedObjectWidget(None)
            self.render(self.objects)
        elif event.key() == QtCore.Qt.Key_C and event.modifiers() & QtCore.Qt.ControlModifier and self.focusedObject:
            # Copy element with CTRL+C
            self.clipboard = deepcopy(self.focusedObject)
        elif event.key() == QtCore.Qt.Key_V and event.modifiers() & QtCore.Qt.ControlModifier and self.clipboard:
            # Paste element with CTRL+V
            # Element index to one to the right
            if isinstance(self.clipboard, MapText):
                self.clipboard.x += 256
                self.pasteTextEvent.emit(self.clipboard)
            elif isinstance(self.clipboard, Element):
                self.clipboard.x += 1
                self.pasteElementEvent.emit(self.clipboard)
            else:
                print("ERROR: Cannot copy unsupported object!")
        elif event.key() == QtCore.Qt.Key_Delete and self.focusedObject:
            if isinstance(self.focusedObject, MapText):
                self.removeTextEvent.emit(self.focusedObject.id)
            elif isinstance(self.focusedObject, Element):
                self.removeElementEvent.emit(self.focusedObject.id)
            else:
                print("ERROR: Cannot delete unsupported object!")
        else:
            super().keyPressEvent(event)

    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        # Things to handle on each render that are not default QT drawing stuff
        # Make sure correct tile has focus
        if self.focusedObject and not self.focusedObjectWidget.hasFocus():
            QtCore.QTimer.singleShot(
                0, lambda: self.focusedObjectWidget.setFocus(QtCore.Qt.OtherFocusReason))

        super().drawForeground(painter, rect)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        # Draw the editor background (grid)
        super().drawBackground(painter, rect)

        # Not rendered in preview
        if self.is_preview:
            return

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

    def _canDrag(self, event: QtGui.QDragEnterEvent | QtGui.QDragMoveEvent):
        # Handle dropped elements
        if event.mimeData().hasText() and event.mimeData().text().startswith("BDM; "):
            event.setDropAction(QtCore.Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(
        self, event: QtGui.QDragEnterEvent): self._canDrag(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent): self._canDrag(event)

    def dropEvent(self, event: QtGui.QDropEvent):  # MARK: Drag Event
        # Triggered when user has picked the location
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
                self.addElementEvent.emit(
                    AddElementEvent(tile_x, tile_y, 1, 1))
                event.accept()
            elif event_mime_text.startswith("BDM; move_element "):
                target_tile = int(event_mime_text.split(" ")[2])
                tile_x = int(scene_pos.x() //
                             self.element_size)
                tile_y = int(scene_pos.y() //
                             self.element_size)
                self.moveElementEvent.emit(
                    MoveElementEvent(target_tile, tile_x, tile_y))
                event.accept()
            elif event_mime_text.startswith("BDM; move_text "):
                target_text = int(event_mime_text.split(" ")[2])

                # Offset point to text center
                text_widget: TextWidget | None = list(filter(
                    lambda obj: obj.id == target_text and obj.type == "text", self.objectWidgets))[0]
                if not text_widget:
                    raise RenderingException(
                        "ERROR: Unable to resolve widget for text to be moved!")

                text_rect = text_widget.rect()
                centered_x = scene_pos.x() - text_rect.width() / 2
                centered_y = scene_pos.y() - text_rect.height() / 2

                self.moveTextEvent.emit(MoveTextEvent(
                    target_text, centered_x, centered_y))
                event.accept()
            elif event_mime_text == "BDM; new_text":
                self.addTextEvent.emit(AddTextEvent(
                    scene_pos.x(), scene_pos.y()))
                event.accept()
            else:
                event.setDropAction(QtCore.Qt.DropAction.IgnoreAction)
                print(
                    f"WARNING: Unsupported drag event, tried: {event_mime_text}")
        else:
            event.ignore()
            print("WARNING: Drag event did not contain data. Ignored.")

    # MARK: Set focus
    def _setFocusedObjectWidget(self, object: TileWidget | TextWidget | None):
        # Set focused object in the editor
        if object == None:
            self.focusedObject = None
            self.focusedObjectWidget = None
            self.focusObjectEvent.emit(FocusEvent(None, None))
        else:
            self.focusedObjectWidget = object
            self.focusedObject = list(filter(
                lambda obj: obj.id == object.id and obj.type == object.type, self.objects))[0]
            if not self.focusedObject:
                raise RenderingException(
                    "ERROR: Object to focus is not in objects cache! Cannot focus.")
            self.focusObjectEvent.emit(FocusEvent(object.id, object.type))
        self.viewport().update()

    def _render_element_object(self, element: Element) -> bool:  # MARK: Render
        # Add grid elements to the map
        # Create tile
        tile = TileWidget(element.x * self.element_size,  # x
                          element.y * self.element_size,  # y
                          self.element_size,  # w
                          self.element_size,  # h
                          tile_id=element.id,
                          background_image=element.background_image.data if element.background_image != None else None,
                          background_color=element.background_color,
                          rotation=element.rotation,
                          is_preview=self.is_preview)

        tile.focusEvent.connect(lambda: self._setFocusedObjectWidget(tile))
        self.scene().addItem(tile)
        self.objectWidgets.append(tile)

        # Update in focus tile
        gave_focus = False
        if self.focusedObject != None and element.id == self.focusedObject.id and self.focusedObject.type == "element":
            gave_focus = True
            self._setFocusedObjectWidget(tile)

        # Only render labels when we are editing
        if not self.is_preview:
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
        text_widget = TextWidget(text.x,  # x
                                 text.y,  # y
                                 1,
                                 1,
                                 text=text,
                                 is_preview=self.is_preview)

        text_widget.focusEvent.connect(
            lambda: self._setFocusedObjectWidget(text_widget))
        self.scene().addItem(text_widget)
        self.objectWidgets.append(text_widget)

        # Update in focus text
        gave_focus = False
        if self.focusedObject != None and text.id == self.focusedObject.id and self.focusedObject.type == "text":
            gave_focus = True
            self._setFocusedObjectWidget(text_widget)

        # Handle focus
        text_widget.focusEvent.connect(
            lambda: self._setFocusedObjectWidget(text_widget))
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
