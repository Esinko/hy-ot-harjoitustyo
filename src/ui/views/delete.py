from PySide6 import QtWidgets, QtCore
from map.abstract import Map
from ui.components.buttons import StandardButtonWidget
from ui.view import View


class DeleteView(View):
    def _delete_map(self, map: Map):
        map.delete()
        self.change_view("select_map")

    def open(self):
        # Change to vertical layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(10)

        label = QtWidgets.QLabel(
            f"Are you sure you want to delete: '{self.context.map.name}'?")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Horizontal layout for buttons
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(10)
        button_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Delete button
        delete_button = StandardButtonWidget("Delete")
        delete_button.clicked.connect(lambda: self._delete_map(self.context.map))

        # Cancel button
        cancel_button = StandardButtonWidget("Cancel")
        cancel_button.clicked.connect(lambda: self.change_view("select_map"))

        button_row.addWidget(cancel_button)
        button_row.addWidget(delete_button)

        self.layout.addWidget(label)
        self.layout.addLayout(button_row)
