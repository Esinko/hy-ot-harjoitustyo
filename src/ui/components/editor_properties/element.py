from PySide6 import QtWidgets, QtCore
from os.path import abspath
from pathlib import Path
from typing import List
from ui.components.editor_sidebar import EditorSidebar
from ui.components.inputs import InputGroupWidget, TextInputWidget, ImageFileInputWidget, DialInputWidget, StandardDropdownWidget, DropdownGroup, SelectedAction, ColorInputWidget
from ui.components.buttons import DeleteButtonWidget, StandardButtonWidget
from map.types import Element, ElementEditable, Asset

default_images = {  # Default images in the image picker
    "Camp": abspath("./ui/images/Camp.jpg"),
    "Corner": abspath("./ui/images/Corner.jpg"),
    "Straight": abspath("./ui/images/Straight.jpg"),
    "Prize Room": abspath("./ui/images/Prize_room.jpg"),
    "3 Point Intersection": abspath("./ui/images/3-point-intersection.jpg"),
    "Straight Infinite Stairs": abspath("./ui/images/Straight_infinite_stairs.jpg")
}


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


class ElementPropertiesWidget(EditorSidebar):
    editElementEvent = QtCore.Signal(EditElementEvent)
    removeElementEvent = QtCore.Signal(RemoveElementEvent)
    target_element: Element | None = None
    name_input: TextInputWidget
    background_input: ImageFileInputWidget
    delete_background_button: DeleteButtonWidget
    delete_button: StandardButtonWidget
    rotation_dial: DialInputWidget
    image_library_picker: StandardDropdownWidget
    available_assets: List[Asset] = []
    color_input: ColorInputWidget

    def setElement(self, element: Element | None):
        # Disable fields
        self.target_element = None

        # Set values
        self.name_input.setDisabled(element is None)
        self.name_input.setText(element.name if element is not None else "")
        self.background_input.setDisabled(element is None)
        if element != None and element.background_image:
            self.background_input.setText(
                f"Image: {element.background_image.name}")
            self.delete_background_button.setDisabled(False)
            self.image_library_picker.setDisabled(True)
        else:
            self.background_input.setText("Select Image")
            self.delete_background_button.setDisabled(True)
            self.image_library_picker.setDisabled(False)
        self.delete_button.setDisabled(element is None)
        self.rotation_dial.setDisabled(element is None)
        self.rotation_dial.setValue(
            element.rotation + 180 if element is not None else 180)
        self.color_input.set_color(
            element.background_color if element else "#8F9092")
        self._build_pick_background_menu()

        # Set target last to prevent emission of changed events
        self.target_element = element

        # If element is none, hide panel
        if element is None:
            self.hide()
        else:
            self.show()

    def setAssets(self, assets: List[Asset]):
        self.available_assets = assets

    def _get_cached_asset(self, id: int) -> Asset | None:
        for asset in self.available_assets:
            if asset.id == id:
                return asset

        return None

    def _edit_name(self):
        if not self.target_element:
            return
        self.target_element.name = self.name_input.text()
        element_editable = self.target_element.to_dict()
        self.editElementEvent.emit(EditElementEvent(
            self.target_element.id, element_editable))

    def _edit_background_image(self, event):
        if not self.target_element:
            return
        element_editable = self.target_element.to_dict()
        if not event:
            # Delete background
            element_editable["background_image"] = None
        else:
            element_editable["background_image"] = {
                "name": event.name,
                "data": list(event.data)
            }
        self.editElementEvent.emit(EditElementEvent(
            self.target_element.id, element_editable))

    def _pick_background_from_library(self, event: SelectedAction):
        # Triggered when default is selected
        element_editable = self.target_element.to_dict()
        element_editable["background_image"] = {
            "name": event["text"],
            "data": self._get_cached_asset(int(event["id"].removeprefix("a-"))).data
            if event["id"].startswith("a-") else
            list(Path(event["id"]).read_bytes())
        }
        self.editElementEvent.emit(EditElementEvent(
            self.target_element.id, element_editable))

    def _delete(self):
        self.removeElementEvent.emit(
            RemoveElementEvent(self.target_element.id))
        self.target_element = None

    def _edit_rotation(self):
        if not self.target_element:
            return
        element_editable = self.target_element.to_dict()
        element_editable["rotation"] = self.rotation_dial.value() - 180
        self.editElementEvent.emit(EditElementEvent(
            self.target_element.id, element_editable))

    def _build_pick_background_menu(self):
        # Builds the dropdown menu
        # We need to re-run this to rebuild the list
        self.image_library_picker.setOptions([
            DropdownGroup(name="Defaults", options=(
                {"text": image_name, "id": default_images[image_name]}
                for image_name in default_images.keys()
            )),
            DropdownGroup(name="Copy", options=(
                {"text": asset.name, "id": f"a-{asset.id}"}
                for asset in self.available_assets
            ))
        ])

    def _edit_color(self):
        if not self.target_element:
            return
        self.target_element.background_color = self.color_input.get_color()
        element_editable = self.target_element.to_dict()
        self.editElementEvent.emit(EditElementEvent(
            self.target_element.id, element_editable))

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hide()

        # Element name
        element_name_label = QtWidgets.QLabel("Tile Name:")
        self.name_input = TextInputWidget()
        self.name_input.textChanged.connect(self._edit_name)
        self.name_input.setDisabled(True)
        self.sidebar_layout.addWidget(element_name_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.sidebar_layout.addWidget(self.name_input)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Element background
        element_background_label = QtWidgets.QLabel("Tile Image:")
        background_row = InputGroupWidget()
        self.background_input = ImageFileInputWidget()
        self.background_input.setDisabled(True)
        self.background_input.selectFileEvent.connect(
            self._edit_background_image)
        background_row.addWidget(self.background_input)
        self.delete_background_button = DeleteButtonWidget(box_size=24)
        self.delete_background_button.clicked.connect(
            self._edit_background_image)
        background_row.addWidget(self.delete_background_button)
        self.sidebar_layout.addWidget(element_background_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.sidebar_layout.addWidget(background_row)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))

        # Default image picker (see function)
        self.image_library_picker = StandardDropdownWidget(
            text="Select Default/Copy")
        self._build_pick_background_menu()
        self.image_library_picker.selectEvent.connect(
            lambda event: self._pick_background_from_library(event))
        self.sidebar_layout.addWidget(self.image_library_picker)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Rotation dial
        element_rotation_label = QtWidgets.QLabel("Content Rotation:")
        self.sidebar_layout.addWidget(element_rotation_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.rotation_dial = DialInputWidget()
        self.rotation_dial.valueChanged.connect(self._edit_rotation)
        self.sidebar_layout.addWidget(self.rotation_dial)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Element color
        color_label = QtWidgets.QLabel("Tile Color:")
        self.color_input = ColorInputWidget()
        self.color_input.color_changed.connect(self._edit_color)
        self.sidebar_layout.addWidget(color_label)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 4))
        self.sidebar_layout.addWidget(self.color_input)
        self.sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 8))

        # Delete element button
        self.delete_button = StandardButtonWidget("Delete Element")
        self.delete_button.clicked.connect(self._delete)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.delete_button)
