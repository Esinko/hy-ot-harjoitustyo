from PySide6 import QtWidgets, QtCore
from ui.components.inputs import TextInputWidget, ImageFileInputWidget
from ui.components.buttons import StandardButtonWidget
from map.abstract import Element, ElementEditable

class EditElementEvent:
    id: int
    element_editable: ElementEditable

    def __init__(self, element_id: int, element_editable: ElementEditable):
        self.id = element_id
        self.element_editable = element_editable

class RemoveElementEvent:
    id: int

    def __init__(self, element_id: int):
        self.id = element_id

class EditorPropertiesWidget(QtWidgets.QWidget):
    editElementEvent = QtCore.Signal(EditElementEvent)
    removeElementEvent = QtCore.Signal(RemoveElementEvent)
    target_element: Element | None = None
    name_input: TextInputWidget
    background_input: ImageFileInputWidget
    delete_button: StandardButtonWidget

    def setElement(self, element: Element | None):
        # Disable fields
        self.target_element = None

        # Set values
        self.name_input.setDisabled(element == None)
        self.name_input.setText(element.name if element != None else "")
        self.background_input.setDisabled(element == None)
        if element != None and element.background_image: self.background_input.setText(f"Image: {element.background_image.name}")
        else: self.background_input.setText("Select Image")
        self.delete_button.setDisabled(element == None)

        # Set target last to prevent emission of changed events
        self.target_element = element

    def _edit_name(self):
        if not self.target_element:
            return
        self.target_element.name = self.name_input.text()
        element_editable = self.target_element.to_dict()
        self.editElementEvent.emit(EditElementEvent(self.target_element.id, element_editable))

    def _edit_background_image(self, event):
        if not self.target_element:
            return
        element_editable = self.target_element.to_dict()
        element_editable["background_image"] = {
            "name": event.name,
            "data": list(event.data)
        }
        self.editElementEvent.emit(EditElementEvent(self.target_element.id, element_editable))

    def _delete(self):
        self.removeElementEvent.emit(RemoveElementEvent(self.target_element.id))
        self.target_element = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("editorSidebar")
        self.setFixedWidth(260)
        self.setStyleSheet("""
            #editorSidebar {
                background-color: #727272;
                border-left: 1px solid black;              
            }
        """)
        sidebar_layout = QtWidgets.QVBoxLayout(self)
        sidebar_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setSpacing(0)

        # Element name
        element_name_label = QtWidgets.QLabel("Tile Name:")
        self.name_input = TextInputWidget()
        self.name_input.textChanged.connect(self._edit_name)
        self.name_input.setDisabled(True)
        sidebar_layout.addWidget(element_name_label)
        sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        sidebar_layout.addWidget(self.name_input)
        sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Element background
        element_background_label = QtWidgets.QLabel("Tile Image:")
        self.background_input = ImageFileInputWidget()
        self.background_input.setDisabled(True)
        self.background_input.selectFileEvent.connect(self._edit_background_image)
        sidebar_layout.addWidget(element_background_label)
        sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        sidebar_layout.addWidget(self.background_input)

        # Delete element button
        self.delete_button = StandardButtonWidget("Delete Element")
        self.delete_button.clicked.connect(self._delete)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.delete_button)