from PySide6 import QtWidgets, QtCore
from map.entity import Map
from ui.components.buttons import StandardButtonWidget
from ui.components.inputs import TextInputWidget
from ui.view import View, Views


class RenameView(View):
    """A view that allows the user to rename a specific map.
    """
    def _rename_map(self, map: Map, new_name: str, goto: Views):
        """Private method called when a specific map is to be renamed.

        Args:
            map (Map): The map to be renamed.
            new_name (str): The new name of the map.
            goto (Views): The view to change to after renaming the map.
        """
        map.set_name(new_name)
        # NOTE: Does not handle all views!
        if goto == "select_map":
            self.change_view("select_map")
        elif goto == "edit_map":
            self.change_view("edit_map", map.map_file.name)

    def open(self):
        # Change to vertical layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(10)

        label = QtWidgets.QLabel(f"Rename Map \"{self.context.map.name}\"")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        name_input = TextInputWidget()
        name_input.setText(self.context.map.name)
        name_input.setPlaceholderText("Enter name")
        name_input.setFixedWidth(200)

        # Horizontal layout for buttons
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(10)
        button_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Create button
        create_button = StandardButtonWidget("Rename")
        create_button.clicked.connect(
            lambda: self._rename_map(self.context.map, name_input.text(), self.context.parameters[0])
        )

        # Cancel button
        cancel_button = StandardButtonWidget("Cancel")
        cancel_button.clicked.connect(lambda: self.change_view(self.context.parameters[0]))

        button_row.addWidget(cancel_button)
        button_row.addWidget(create_button)

        self.layout.addWidget(label)
        self.layout.addWidget(
            name_input, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(button_row)
