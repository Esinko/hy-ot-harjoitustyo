from uuid import uuid4
from PySide6 import QtWidgets, QtCore
from map.abstract import MapStore
from ui.components.buttons import StandardButtonWidget
from ui.components.inputs import TextInputWidget
from ui.view import View


class CreateView(View):
    def _create_map(self, map_store: MapStore, name: str):
        if len(name) > 0:
            map_store.create_map(name, f"{uuid4()}.dmap")
            self.change_view("select_map")  # TODO: Change to editor?

    def open(self):
        # Change to vertical layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(10)

        # Pick map label
        label = QtWidgets.QLabel("Pick Map Name")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        name_input = TextInputWidget()
        name_input.setPlaceholderText("Enter name")
        name_input.setFixedWidth(200)

        # Horizontal layout for buttons
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(10)
        button_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Create button
        create_button = StandardButtonWidget("Create")
        create_button.clicked.connect(
            lambda: self._create_map(self.context.map_store,
                                     name_input.text()))

        # Cancel button
        cancel_button = StandardButtonWidget("Cancel")
        cancel_button.clicked.connect(lambda: self.change_view("select_map"))

        button_row.addWidget(cancel_button)
        button_row.addWidget(create_button)

        self.layout.addWidget(label)
        self.layout.addWidget(
            name_input, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(button_row)
