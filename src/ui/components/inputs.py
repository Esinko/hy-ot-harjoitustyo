from PySide6 import QtWidgets, QtGui, QtCore
from os.path import abspath
from ui.components.buttons import StandardButtonWidget
from pathlib import Path


class TextInputWidget(QtWidgets.QLineEdit):
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
    # TODO: Convert to group, add filename in read-only text line, then add X and select buttons on the right
    selectFileEvent = QtCore.Signal(SelectFileEvent)

    def _select_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        self.selectFileEvent.emit(SelectFileEvent(file_path))

    def __init__(self, parent=None):
        super().__init__(text="Select Image", parent=parent)
        self.clicked.connect(self._select_file)

class DialInputWidget(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)
    def __init__(self, step=10, *args, **kwargs):
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
        self.dial.valueChanged.connect(self.updateValue)

    def updateValue(self):
        # Handle updating the dial value in a stepped fashion
        stepped_value = round(self.dial.value(), -1)
        self.dial.blockSignals(True) # Block signals to prevent a loop
        self.setValue(stepped_value)
        self.dial.blockSignals(False)
        self.label.setText(f"{stepped_value - 180} deg")
        self.valueChanged.emit(stepped_value)
    
    # Standard for dial
    def setValue(self, value):
        self.dial.setValue(value)

    # Standard for dial
    def value(self) -> int:
        return self.dial.value()
    
    # Standard for dial
    def setDisabled(self, disabled: bool):
        self.dial.setDisabled(disabled)

class InputGroupWidget(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(5)
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
        self.layout().addWidget(widget)


class DragNumberInputWidget(QtWidgets.QLineEdit):
    drag_step: int
    min: int | None
    max: int | None
    _dragging: bool
    _drag_start_value: int
    _drag_start_x: int

    def __init__(self, parent = None, drag_step = 1, min_value: int | None = None, max_value: int | None = None):
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
        self.addAction(left_icon, QtWidgets.QLineEdit.ActionPosition.LeadingPosition)
        self.addAction(right_icon, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)

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

    # Override press event to begin dragging
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

    # Handle changing value while dragging
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

    # Handle end during dragging
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
    colorChanged = QtCore.Signal(str)
    color: QtGui.QColor
    colorPreview: QtWidgets.QWidget

    def __init__(self, initial_color="#FF0000"):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.color = QtGui.QColor(initial_color)

        # Color preview
        self.colorPreview = QtWidgets.QWidget()
        self.colorPreview.setAutoFillBackground(True)
        self.colorPreview.setFixedSize(22, 22)
        self.addWidget(self.colorPreview)

        # Open button
        open_button = StandardButtonWidget("Pick Color")
        open_button.clicked.connect(self.choose_color)
        self.addWidget(open_button)
        self.update_style()

    def choose_color(self):
        color = QtWidgets.QColorDialog.getColor(self.color, self.parentWidget())
        if color.isValid():
            self.color = color
            self.colorChanged.emit(color)
            self.update_style()

    def setColor(self, color: str):
        self.color = QtGui.QColor(color)
        self.update_style()

    def getColor(self) -> str:
        return self.color.name()

    def update_style(self):
        self.colorPreview.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #393939;")