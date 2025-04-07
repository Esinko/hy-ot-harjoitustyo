from PySide6 import QtWidgets, QtGui, QtCore
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