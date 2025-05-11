from PySide6 import QtWidgets, QtGui, QtCore
from os.path import abspath
from dataclasses import dataclass
from ui.components.buttons import StandardButtonWidget
from pathlib import Path
from typing import List, TypedDict


class TextInputWidget(QtWidgets.QLineEdit):
    """A styled text input.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("""
            QLineEdit {
                color: black;
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #B0B0B0, stop:1 #999999);
                border: 1px solid #393939;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:hover {
                border-color: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #FDA239, stop:1 #F0851B);
            }
        """)


class TextAreaInputWidget(QtWidgets.QTextEdit):
    """A styled text area.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setStyleSheet("""
            QTextEdit {
                color: black;
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #B0B0B0, stop:1 #999999);
                border: 1px solid #393939;
                border-radius: 4px;
                padding: 4px;
            }
            QTextEdit:hover {
                border-color: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #FDA239, stop:1 #F0851B);
            }
        """)


class SelectFileEvent:
    file: Path
    name: str
    data: bytes

    def __init__(self, file_path):
        # TODO: Handle read issue here?
        self.file = Path(file_path)
        self.data = self.file.read_bytes()
        self.name = self.file.name


class ImageFileInputWidget(StandardButtonWidget):
    """A styled image file input.
    """
    selectFileEvent = QtCore.Signal(SelectFileEvent)

    def _select_file(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        dialog.setWindowTitle("Select Image")

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            file_path = dialog.selectedFiles()[0]
            self.selectFileEvent.emit(SelectFileEvent(file_path))

    def __init__(self, parent=None):
        super().__init__(text="Select Image", parent=parent)
        self.clicked.connect(self._select_file)


class DialInputWidget(QtWidgets.QWidget):
    """A styled dial with full 360-range.
    """
    valueChanged = QtCore.Signal(int)

    def __init__(self, step=10, *args, **kwargs):
        """The constructor of the styled dial input.

        Args:
            step (int): The granularity of the dial step. Defaults to 10.
        """
        super().__init__(*args, **kwargs)
        self.dial = QtWidgets.QDial()
        self.label = QtWidgets.QLabel("0 deg")
        self.dial.setFixedSize(50, 50)
        self.dial.setRange(0, 360)
        self.dial.setWrapping(True)
        self.dial.setSingleStep(step)
        self.dial.setPageStep(step)
        self.dial.setDisabled(True)
        self.dial.setStyleSheet("""
            QDial {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #B0B0B0, stop:1 #999999);
                border: 1px solid #393939;
                padding: 4px;
            }
        """)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.dial)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.dial.valueChanged.connect(self._updateValue)

    def _updateValue(self):
        """Handle the updating of the dial value.
        """
        # Handle updating the dial value in a stepped fashion
        stepped_value = round(self.dial.value(), -1)
        self.dial.blockSignals(True)  # Block signals to prevent a loop
        self.setValue(stepped_value)
        self.dial.blockSignals(False)
        self.label.setText(f"{stepped_value - 180} deg")
        self.valueChanged.emit(stepped_value)

    def setValue(self, value: int):
        """Set the value of the dial. Causes an update event!

        Args:
            value (int): The new value of the dial.
        """
        self.dial.setValue(value)

    def value(self) -> int:
        """Get the value of the dial.

        Returns:
            int: The value of the dial
        """
        return self.dial.value()

    def setDisabled(self, disabled: bool):
        """Enable/Disable user interaction on the dial.

        Args:
            disabled (bool): True to disable the dial.
        """
        self.dial.setDisabled(disabled)


class InputGroupWidget(QtWidgets.QFrame):
    """A horizontal input group.
    """

    def __init__(self):
        super().__init__()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("inputGroup")
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
            #inputGroup {
                padding: 0px;
                border: 0px;
            }
        """)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(button_layout)

    # Standard from layout
    def addWidget(self, widget):
        """Add a new widget to the group.

        Args:
            widget: The widget to add to the group.
        """
        self.layout().addWidget(widget)


class DragNumberInputWidget(QtWidgets.QLineEdit):
    """A number input that allows horizontal mouse dragging to change the value along with regular edit.

    Attributes:
        drag_step (int): The granularity of the drag step
        min (int, optional): Minimum value of the input
        max (int, optional): Maximum value of the input
    """
    drag_step: int
    min: int | None
    max: int | None
    _dragging: bool
    _drag_start_value: int
    _drag_start_x: int

    def __init__(self, parent=None, drag_step=1, min_value: int | None = None, max_value: int | None = None):
        """Constructor of the drag-number-input

        Args:
            drag_step (int): The drag step. Defaults to 1.
            min_value (int, optional): The minimum value of the input.
            max_value (int, optional): The maximum value of the input.
        """
        super().__init__(parent=parent)
        self.drag_step = drag_step
        self.min = min_value
        self.max = max_value
        self._dragging = False
        self._drag_start_value = 0
        self._drag_start_x = 0

        # Only allow ints
        validator = QtGui.QIntValidator()
        self.setValidator(validator)
        self.setText("0")

        # Add icons on the left and the right
        left_icon = QtGui.QIcon(abspath("./ui/icons/chevron-left.svg"))
        right_icon = QtGui.QIcon(abspath("./ui/icons/chevron-right.svg"))
        self.addAction(
            left_icon, QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        self.addAction(
            right_icon, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)

        # Styling
        self.setCursor(QtCore.Qt.SizeHorCursor)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.setStyleSheet("""
            QLineEdit {
                color: black;
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #B0B0B0, stop:1 #999999);
                border: 1px solid #393939;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:hover {
                border-color: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #FDA239, stop:1 #F0851B);
            }
        """)

    # Override press event to begin dragging (QT override)
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = True
            self.blockSignals(True)
            self._drag_start_x = event.globalX()
            self._drag_start_value = int(self.text())
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    # Handle changing value while dragging (QT override)
    def mouseMoveEvent(self, event):
        if self._dragging:
            dx = event.globalX() - self._drag_start_x
            delta = dx * self.drag_step
            new_value = round(self._drag_start_value + delta, 0)
            if new_value < self.min:
                new_value = self.min
            elif new_value > self.max:
                new_value = self.max
            self.setText(str(new_value))
            event.accept()
        else:
            super().mouseMoveEvent(event)

    # Handle end during dragging (QT override)
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self.blockSignals(False)
            self.textChanged.emit(self.text())
            self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class ColorInputWidget(InputGroupWidget):
    """Color input widget with native color picker and preview.

    Attributes:
        color_changed (Signal): Signal emitted when the color changes
        color (QColor): The current color of the input
        color_preview (QWidget): The preview widget
    """
    color_changed = QtCore.Signal(str)
    color: QtGui.QColor
    color_preview: QtWidgets.QWidget

    def __init__(self, initial_color="#FF0000"):
        """Constructor of the color input

        Args:
            initial_color (str, optional): The initial color in the input. Defaults to "#FF0000".
        """
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.color = QtGui.QColor(initial_color)

        # Color preview
        self.color_preview = QtWidgets.QWidget()
        self.color_preview.setAutoFillBackground(True)
        self.color_preview.setFixedSize(22, 22)
        self.addWidget(self.color_preview)

        # Open button
        open_button = StandardButtonWidget("Pick Color")
        open_button.clicked.connect(self._choose_color)
        self.addWidget(open_button)
        self._update_style()

    def _choose_color(self):
        """Private method that opens the native OS provided color picker.
        """
        dialog = QtWidgets.QColorDialog(parent=self.parentWidget())
        dialog.setOption(QtWidgets.QColorDialog.ColorDialogOption.DontUseNativeDialog)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            color = dialog.selectedColor()
            if color.isValid():
                self.color = color
                self.color_changed.emit(color)
                self._update_style()

    def set_color(self, color: str):
        """Set the color of the input.

        Args:
            color (str): The hex color to be set.
        """
        self.color = QtGui.QColor(color)
        self._update_style()

    def get_color(self) -> str:
        """Get the current hex color value of the input.

        Returns:
            str: The hex color of the input.
        """
        return self.color.name()

    def _update_style(self):
        """Internal method that updates the preview's color to match the input.
        """
        self.color_preview.setStyleSheet(
            f"background-color: {self.color.name()}; border: 1px solid #393939;")


class ComplexOption(TypedDict):
    id: str | int | None
    text: str


class SelectedAction(ComplexOption):
    item_index: int
    group_index: int


@dataclass
class DropdownGroup:
    name: str
    options: List[ComplexOption | str]


class StandardDropdownWidget(QtWidgets.QWidget):
    """Dropdown styled to look like a button. Drop-in replacement for ComboBox."""

    selectEvent = QtCore.Signal(ComplexOption)
    currentIndexChanged = QtCore.Signal(int)

    def _fallback_signal(self, i: int, text: str):
        self.currentIndexChanged.emit(i)
        self.button.setText(text)

    def __init__(
        self,
        text: str | None = None,
        options: List[DropdownGroup | str] = []
    ):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create menu button
        self.button = QtWidgets.QToolButton(self)
        self.button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.button.setStyleSheet("""
            QToolButton {
                color: white;
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #373737, stop:1 #535353);
                border: 1px solid #292929;
                border-radius: 4px;
                padding: 4px 28px 4px 8px;
                text-align: left;
            }
            QToolButton:hover, QToolButton:focus {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #FDA239, stop:1 #F0851B);
            }
            QToolButton::menu-indicator {
                image: url(ui/icons/chevron-down.svg);
                width: 14px; height: 14px;
                subcontrol-position: right center;
                padding-left: 4px; padding-right: 4px;
                border-left: 1px solid #292929;
            }
            QToolButton:disabled {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #535353, stop:1 #646464);
            }
        """)

        # Add button value
        if not text and options and isinstance(options[0], str):
            self.button.setText(options[0])
        else:
            self.button.setText(text or "")

        # Create menu
        self.menu = QtWidgets.QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background: transparent;
                border: 1px solid #292929;
                color: white;
            }
        """)

        # Create item container
        self._scroll_container = QtWidgets.QWidget()
        self._scroll_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                        stop:0 #373737, stop:1 #535353);
        """)
        self._scroll_layout = QtWidgets.QVBoxLayout(self._scroll_container)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(0)

        # Create scroll area
        self._scroll_area = QtWidgets.QScrollArea()
        self._scroll_area.setWidget(self._scroll_container)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self._scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._scroll_area.setMaximumHeight(200)

        # Add scroll area to menu
        scroll_action = QtWidgets.QWidgetAction(self.menu)
        scroll_action.setDefaultWidget(self._scroll_area)
        self.menu.addAction(scroll_action)
        self.button.setMenu(self.menu)
        layout.addWidget(self.button)

        # populate initial options
        self.setOptions(options)

    def setOptions(self, options: List[DropdownGroup | str] = []):
        # Remove old buttons
        while self._scroll_layout.count():
            item = self._scroll_layout.takeAt(0)
            if w := item.widget():
                w.deleteLater()

        action_button_style = """
            QPushButton, QLabel {
                text-align: left;
                padding: 6px 24px 6px 12px;
                border: none;
                background: transparent;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                            stop:0 #FDA239, stop:1 #F0851B);
            }
        """

        # Build items
        for i, group in enumerate(options):
            if hasattr(group, "name") and hasattr(group, "options"):
                # Group name
                header = QtWidgets.QLabel(group.name)
                header.setStyleSheet("""
                    color: white;
                    padding: 4px 28px 4px 8px;
                    background: transparent;
                    font-size: 11px;
                    font-weight: bold;
                """)
                self._scroll_layout.addWidget(header)

                # Create buttons for this group
                for j, opt in enumerate(group.options):
                    txt = opt["text"] if isinstance(opt, dict) else opt
                    action_button = QtWidgets.QPushButton(txt)
                    action_button.setFlat(True)
                    action_button.setCursor(QtCore.Qt.PointingHandCursor)
                    action_button.setStyleSheet(action_button_style)
                    action_button.clicked.connect(
                        lambda _, gi=i, ii=j, option=opt, txt=txt: (
                            self.selectEvent.emit({
                                "group_index": gi,
                                "item_index": ii,
                                "id": option.get("id") if isinstance(option, dict) else None,
                                "text": txt
                            }),
                            self.menu.hide()
                        )
                    )
                    self._scroll_layout.addWidget(action_button)

                    # Button border
                    if j != len(group.options) - 1:
                        line = QtWidgets.QFrame()
                        line.setFrameShape(QtWidgets.QFrame.HLine)
                        line.setFrameShadow(QtWidgets.QFrame.Sunken)
                        line.setStyleSheet("background: #292929;")
                        line.setFixedHeight(1)
                        self._scroll_layout.addWidget(line)
            else:
                # Fallback to simple options
                action_button = QtWidgets.QPushButton(group)
                action_button.setFlat(True)
                action_button.setCursor(QtCore.Qt.PointingHandCursor)
                action_button.setStyleSheet(action_button_style)
                action_button.clicked.connect(
                    lambda _, idx=i, txt=group: (
                        self._fallback_signal(idx, txt),
                        self.menu.hide()
                    )
                )
                self._scroll_layout.addWidget(action_button)

            # Group separator
            if i != len(options) - 1:
                line = QtWidgets.QFrame()
                line.setFrameShape(QtWidgets.QFrame.HLine)
                line.setFrameShadow(QtWidgets.QFrame.Sunken)
                line.setStyleSheet("margin: 4px 0; background: #292929;")
                self._scroll_layout.addWidget(line)
