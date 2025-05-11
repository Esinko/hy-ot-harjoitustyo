from PySide6 import QtWidgets, QtCore
from map.types import MapText, TextEditable
from ui.components.editor_sidebar import EditorSidebar
from ui.components.inputs import ColorInputWidget, DragNumberInputWidget, TextAreaInputWidget, TextInputWidget, DialInputWidget
from ui.components.buttons import StandardButtonWidget


class EditTextEvent:
    id: int
    text_editable: TextEditable

    def __init__(self, text_id: int, text_editable: TextEditable):
        self.id = text_id
        self.text_editable = text_editable


class RemoveTextEvent:
    id: int

    def __init__(self, element_id: int):
        self.id = element_id


class TextPropertiesWidget(EditorSidebar):
    editTextEvent = QtCore.Signal(EditTextEvent)
    removeTextEvent = QtCore.Signal(RemoveTextEvent)
    target_text: MapText | None = None
    name_input: TextInputWidget
    value_input: TextAreaInputWidget
    delete_button: StandardButtonWidget
    rotation_dial: DialInputWidget
    font_size_input: DragNumberInputWidget
    color_input: ColorInputWidget

    def setText(self, text: MapText | None):
        # Disable fields
        self.target_text = None

        # Set values
        self.name_input.setDisabled(text is None)
        self.name_input.setText(text.name if text is not None else "")
        self.value_input.setPlainText(text.value if text is not None else "")
        self.value_input.setDisabled(text is None)
        self.delete_button.setDisabled(text is None)
        self.rotation_dial.setDisabled(text is None)
        self.rotation_dial.setValue(
            text.rotation + 180 if text is not None else 180)
        self.font_size_input.setText(
            str(text.font_size) if text is not None else "")
        self.font_size_input.setDisabled(text is None)
        self.color_input.set_color(text.color if text is not None else "#000")
        self.color_input.setDisabled(text is None)

        # Set target last to prevent emission of changed events
        self.target_text = text

        # If tex is none, hide panel
        if text is None:
            self.hide()
        else:
            self.show()

    def _edit_name(self):
        if not self.target_text:
            return
        self.target_text.name = self.name_input.text()
        text_editable = self.target_text.to_dict()
        self.editTextEvent.emit(EditTextEvent(
            self.target_text.id, text_editable))

    def _edit_value(self):
        if not self.target_text:
            return
        self.target_text.value = self.value_input.toPlainText()
        text_editable = self.target_text.to_dict()
        self.editTextEvent.emit(EditTextEvent(
            self.target_text.id, text_editable))

    def _edit_font_size(self):
        if not self.target_text:
            return
        try:
            self.target_text.font_size = int(self.font_size_input.text())
        except ValueError:
            # Ignore value errors, field is empty or NaN
            return
        text_editable = self.target_text.to_dict()
        self.editTextEvent.emit(EditTextEvent(
            self.target_text.id, text_editable))

    def _edit_color(self):
        if not self.target_text:
            return
        self.target_text.color = self.color_input.get_color()
        text_editable = self.target_text.to_dict()
        self.editTextEvent.emit(EditTextEvent(
            self.target_text.id, text_editable))

    def _delete(self):
        self.removeTextEvent.emit(
            RemoveTextEvent(self.target_text.id))
        self.target_text = None

    def _edit_rotation(self):
        if not self.target_text:
            return
        text_editable = self.target_text.to_dict()
        text_editable["rotation"] = self.rotation_dial.value() - 180
        self.editTextEvent.emit(EditTextEvent(
            self.target_text.id, text_editable))

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hide()

        # Text name
        text_name_label = QtWidgets.QLabel("Text Name:")
        self.name_input = TextInputWidget()
        self.name_input.textChanged.connect(self._edit_name)
        self.name_input.setDisabled(True)
        self.sidebar_layout.addWidget(text_name_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.sidebar_layout.addWidget(self.name_input)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Text value
        text_value_label = QtWidgets.QLabel("Text Value:")
        self.value_input = TextAreaInputWidget()
        self.value_input.textChanged.connect(self._edit_value)
        self.value_input.setDisabled(True)
        self.sidebar_layout.addWidget(text_value_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.sidebar_layout.addWidget(self.value_input)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Text font size
        font_size_label = QtWidgets.QLabel("Text Font Size:")
        self.font_size_input = DragNumberInputWidget(
            min_value=0, max_value=300)
        self.font_size_input.setFixedWidth(110)
        self.font_size_input.textChanged.connect(self._edit_font_size)
        self.sidebar_layout.addWidget(font_size_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.sidebar_layout.addWidget(self.font_size_input)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Text color
        color_label = QtWidgets.QLabel("Text Color:")
        self.color_input = ColorInputWidget()
        self.color_input.color_changed.connect(self._edit_color)
        self.sidebar_layout.addWidget(color_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.sidebar_layout.addWidget(self.color_input)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Rotation dial
        text_rotation_label = QtWidgets.QLabel("Text Rotation:")
        self.sidebar_layout.addWidget(text_rotation_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.rotation_dial = DialInputWidget()
        self.rotation_dial.valueChanged.connect(self._edit_rotation)
        self.sidebar_layout.addWidget(self.rotation_dial)

        # Delete text button
        self.delete_button = StandardButtonWidget("Delete Text")
        self.delete_button.clicked.connect(self._delete)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.delete_button)
