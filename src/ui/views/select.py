from posixpath import abspath
from PySide6 import QtWidgets, QtCore, QtGui
from ui.components.buttons import DeleteButtonWidget, ExportMapButton, ImportMapButton, RenameButtonWidget, SelectPathEvent, StandardButtonWidget
from ui.components.editor import EditorGraphicsView
from ui.components.inputs import InputGroupWidget, SelectFileEvent
from ui.view import View


class SelectView(View):
    """Allows the user to select the map to edit and trigger actions against specific maps from the UI.
    """

    def _export_map(self, option, event: SelectPathEvent):
        """Private method called when the user wants to export a specific map.

        Args:
            option: The selected option (map)
            event (SelectPathEvent): The selected path provided by the OS's path select popup.
        """
        self.context.map_store.export(
            self.context.map_store.get(option["id"]),
            event.path
        )

    def _import_map(self, event: SelectFileEvent):
        """Private method called when the user wants to import a map from a specific location.

        Args:
            event (SelectFileEvent): The selected file provided by the OS's path select popup.
        """
        self.context.map_store.add(event.file.absolute())
        self.change_view("select_map")  # Refreshes the view

    def open(self):
        # Change to horizontal layout
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Left panel
        left_panel = QtWidgets.QWidget()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet(
            "background-color: #727272; border-right: 1px solid #000")
        left_layout = QtWidgets.QVBoxLayout(left_panel)

        # Title above scroll area
        select_title = QtWidgets.QLabel("Select Map")
        select_title.setStyleSheet("color: black; border-right: 0px;")
        select_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(select_title)

        # Scroll area for options
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            "QScrollArea { border: 1px solid #393939; border-right: 0px; }")
        scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_content = QtWidgets.QWidget()
        options_layout = QtWidgets.QVBoxLayout(scroll_content)
        options_layout.setSpacing(10)
        options_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # Add all options
        if len(self.context.parameters[0]) == 0:
            options_layout.addWidget(QtWidgets.QLabel("No maps to list."))
        else:
            # Build option row for each map
            for option in self.context.parameters[0]:
                option_row = InputGroupWidget()

                # Open button
                option_button = StandardButtonWidget(option["text"],
                                                     icon=QtGui.QIcon(abspath("./ui/icons/map.svg")))
                option_button.setMaximumWidth(180)
                option_button.clicked.connect(
                    lambda _, opt_id=option["id"]: self.change_view("edit_map", opt_id))

                # Rename button
                rename_button = RenameButtonWidget(24)
                rename_button.clicked.connect(
                    lambda _, opt_id=option["id"]: self.change_view("rename_map", (opt_id, "select_map")))

                # Share button
                share_button = ExportMapButton(
                    24, placeholder_name=f"{option["text"]}.dmap")
                share_button.selectPathEvent.connect(
                    lambda event: self._export_map(option, event))

                # Delete button
                delete_button = DeleteButtonWidget(24)
                delete_button.clicked.connect(
                    lambda _, opt_id=option["id"]: self.change_view("delete_map", opt_id))

                option_row.addWidget(option_button)
                option_row.addWidget(rename_button)
                option_row.addWidget(share_button)
                option_row.addWidget(delete_button)
                options_layout.addWidget(option_row)

        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)

        # Button area
        button_container = QtWidgets.QWidget()
        button_container.setStyleSheet("border-right: 0px;")
        button_container.setFixedHeight(50)
        button_row = QtWidgets.QHBoxLayout(button_container)
        button_row.setSpacing(10)

        # Import button
        import_button = ImportMapButton()
        import_button.selectFileEvent.connect(
            lambda event: self._import_map(event))
        button_row.addWidget(import_button)

        # Create button
        create_button = StandardButtonWidget("Create Map")
        create_button.clicked.connect(lambda: self.change_view("create_map"))
        button_row.addWidget(create_button)

        left_layout.addWidget(button_container)
        self.layout.addWidget(left_panel)

        # Preview in the right
        editor_area = EditorGraphicsView(is_preview=False)
        editor_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        editor_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.layout.addWidget(editor_area)
