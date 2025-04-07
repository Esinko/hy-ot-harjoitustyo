from PySide6 import QtCore, QtWidgets, QtGui
from sys import exit
from typing import List, TypedDict, Literal, Callable, Any
from map.abstract import MapStore, Map, ElementEditable
from uuid import uuid4
from ui.components.editor import EditorGraphicsView
from ui.components.buttons import AddElementButtonWidget, StandardButtonWidget, DeleteButtonWidget
from ui.components.editor_properties import EditorPropertiesWidget

views = Literal["select_map", "create_map", "delete_map", "edit_map"]
view_changer = Callable[[views, Any], None]


class SelectOption(TypedDict):
    id: str
    text: str


class BaseWindow(QtWidgets.QWidget):
    change_view: view_changer

    def __init__(self, change_view: QtCore.Slot):
        super().__init__()
        self.setWindowTitle("Blocky Dungeon Mapper")
        self.change_view = change_view

        # Placeholder
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(QtWidgets.QLabel(
            "Loading ...", alignment=QtCore.Qt.AlignCenter))

    def _create_map(self, map_store: MapStore, name: str):
        if len(name) > 0:
            map_store.create_map(name, f"{uuid4()}.dmap")
            self.change_view("select_map")  # TODO: Change to editor

    def _delete_map(self, map: Map):
        map.delete()
        self.change_view("select_map")

    def _create_element(self, map: Map, x: int, y: int):
        map.create_element({
            "name": "Unnamed Tile",
            "x": x,
            "y": y,
            "width": 1,
            "height": 1
        })

    def _move_element(self, map: Map, id: int, x: int, y: int):
        edited_element = map.get_element(id).to_dict()
        edited_element["x"] = x
        edited_element["y"] = y
        map.edit_element(id, edited_element)

    def clear_window(self):
        old_layout = self.layout
        if not old_layout:
            return

        # Loop over all, event nested, widgets, and delete
        while old_layout.count():
            item = old_layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.deleteLater()
            if child_layout:
                while child_layout.count():
                    sub_item = child_layout.takeAt(0)
                    sub_widget = sub_item.widget()
                    if sub_widget:
                        sub_widget.deleteLater()
                del child_layout

        # Now detach old layout
        QtWidgets.QWidget().setLayout(old_layout)

    def open_editor_view(self, map: Map):
        # Change to vertical layout
        self.clear_window()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.layout.setSpacing(0)

        # Create top row
        top_bar = QtWidgets.QWidget()
        top_bar.setStyleSheet("background-color: #686868")
        top_bar.setFixedHeight(32)
        top_bar_layout = QtWidgets.QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(5, 3, 5, 3)
        top_bar_layout.setSpacing(3)

        # Map name on the left
        map_name = QtWidgets.QLabel(f"Map: {map.name}")
        map_name_font = map_name.font()
        map_name_font.setPointSize(10)
        map_name.setFont(map_name_font)

        # Right side of top row
        top_bar_right = QtWidgets.QWidget()
        top_bar_right_layout = QtWidgets.QHBoxLayout(top_bar_right)
        top_bar_right_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_right_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        autosave_label = QtWidgets.QLabel("Autosaving is enabled.")
        autosave_font = autosave_label.font()
        autosave_font.setPointSize(8)
        autosave_font.setItalic(True)
        autosave_label.setFont(autosave_font)
        top_bar_right_layout.addWidget(autosave_label)

        close_button = StandardButtonWidget("Close")
        close_button.clicked.connect(lambda: self.change_view("select_map"))
        top_bar_right_layout.addWidget(close_button)

        # Join top bar sides
        top_bar_layout.addWidget(map_name)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(top_bar_right)

        # Create tools row
        toolbar = QtWidgets.QWidget()
        toolbar.setStyleSheet(
            "background-color: #727272; border-bottom: 1px solid black;")
        toolbar.setFixedHeight(40)
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 0, 5, 0)
        toolbar_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Add element button
        add_element = AddElementButtonWidget()
        toolbar_layout.addWidget(add_element)

        # Create main editor area (100% <-> x split)
        main = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Actual editor area
        editor_area = EditorGraphicsView()
        editor_area.addElementEvent.connect(
            lambda event: self._create_element(map, event.x, event.y))
        editor_area.moveElementEvent.connect(
            lambda event: self._move_element(map, event.id, event.x, event.y))
        editor_area.render(map.get_elements())  # Initial pass
        map.register_on_change(lambda: editor_area.render(
            map.get_elements()))  # When elements change, this is ran
        main_layout.addWidget(editor_area)

        # Properties side bar
        sidebar = EditorPropertiesWidget()
        editor_area.focusElementEvent.connect(
            lambda event: sidebar.setElement(map.get_element(
                event.id)) if event.id != None else sidebar.setElement(None)
        )
        sidebar.editElementEvent.connect(
            lambda event: map.edit_element(event.id, event.element_editable)
        )
        sidebar.removeElementEvent.connect(
            lambda event: map.remove_element(event.id)
        )
        main_layout.addWidget(sidebar)

        self.layout.addWidget(top_bar)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(main)

    def open_create_view(self, map_store: MapStore):
        # Change to vertical layout
        self.clear_window()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(10)

        label = QtWidgets.QLabel("Pick Map Name")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        name_input = QtWidgets.QLineEdit()
        name_input.setPlaceholderText("Enter name")
        name_input.setFixedWidth(200)

        # Horizontal layout for buttons
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(10)
        button_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Create button
        create_button = QtWidgets.QPushButton("Create")
        create_button.clicked.connect(
            lambda: self._create_map(map_store, name_input.text()))

        # Cancel button
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.change_view("select_map"))

        button_row.addWidget(cancel_button)
        button_row.addWidget(create_button)

        self.layout.addWidget(label)
        self.layout.addWidget(
            name_input, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(button_row)

    def open_delete_view(self, map: Map):
        # Change to vertical layout
        self.clear_window()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(10)

        label = QtWidgets.QLabel(
            f"Are you sure you want to delete: '{map.name}'?")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Horizontal layout for buttons
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(10)
        button_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Delete button
        delete_button = QtWidgets.QPushButton("Delete")
        delete_button.clicked.connect(lambda: self._delete_map(map))

        # Cancel button
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.change_view("select_map"))

        button_row.addWidget(cancel_button)
        button_row.addWidget(delete_button)

        self.layout.addWidget(label)
        self.layout.addLayout(button_row)

    def open_select_view(self, options: List[SelectOption]):
        # Change to horizontal layout
        self.clear_window()
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.layout)

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
        options_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # Add all options
        if len(options) == 0:
            options_layout.addWidget(QtWidgets.QLabel("No maps to list."))
        else:
            for option in options:
                option_row = QtWidgets.QWidget()
                option_row.setStyleSheet("border-right: 0px;")
                row_layout = QtWidgets.QHBoxLayout(option_row)
                row_layout.setContentsMargins(0, 0, 0, 0)

                option_button = StandardButtonWidget(option["text"])
                option_button.setCursor(QtGui.QCursor(
                    QtCore.Qt.CursorShape.PointingHandCursor))
                option_button.clicked.connect(
                    lambda _, opt_id=option["id"]: self.change_view("edit_map", opt_id))

                delete_button = DeleteButtonWidget(24)
                delete_button.clicked.connect(
                    lambda: self.change_view("delete_map", option["id"]))

                row_layout.addWidget(option_button)
                row_layout.addWidget(delete_button)
                options_layout.addWidget(option_row)

        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)

        # Button area
        button_container = QtWidgets.QWidget()
        button_container.setStyleSheet("border-right: 0px;")
        button_container.setFixedHeight(50)
        button_row = QtWidgets.QHBoxLayout(button_container)
        button_row.setSpacing(10)
        button_row.addStretch()
        button_row.addWidget(StandardButtonWidget("Import"))
        button_row.addWidget(StandardButtonWidget("Export"))
        create_button = StandardButtonWidget("Create")
        create_button.clicked.connect(lambda: self.change_view("create_map"))
        button_row.addWidget(create_button)
        button_row.addStretch()

        left_layout.addWidget(button_container)
        self.layout.addWidget(left_panel)
        self.layout.addSpacing(15)

        # Placeholder for preview on the right
        red_square = QtWidgets.QLabel("")
        red_square.setFixedSize(400, 400)
        red_square.setStyleSheet("background: red;")
        self.layout.addWidget(red_square)


class Application:
    _app: QtWidgets.QApplication
    window: BaseWindow
    map_store: MapStore

    def __init__(self, map_store: MapStore):
        self._app = QtWidgets.QApplication([])
        self.window = BaseWindow(self.change_to_view)
        self.map_store = map_store

    # Handle changing application views
    # TODO: Would it be better to store all the parameters in the BaseWindow class as privates?
    # TODO: Separate each view to their own classes?
    def change_to_view(self, view_name: views, option: Any = None):
        if view_name == "select_map":
            self.window.open_select_view(
                [{"id": i, "text": map.name} for i, map in enumerate(self.map_store.list())])
        elif view_name == "create_map":
            self.window.open_create_view(self.map_store)
        elif view_name == "delete_map":
            # TODO: Get specific map by id
            map_to_delete = self.map_store.list(no_refresh=True)[option]
            self.window.open_delete_view(map_to_delete)
        elif view_name == "edit_map":
            # TODO: Get specific map by id
            map_to_edit = self.map_store.list(no_refresh=True)[option]
            self.window.open_editor_view(map_to_edit)

    # Open the main window
    def open(self, width: int = 800, height: int = 600):
        self.window.resize(width, height)
        self.window.show()

        # Prompt the user to select maps
        self.change_to_view("select_map")

        # Make python wait for window to close before exiting
        exit(self._app.exec())
