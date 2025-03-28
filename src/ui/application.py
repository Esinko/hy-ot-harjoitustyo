from PySide6 import QtCore, QtWidgets, QtGui
from sys import exit
from typing import List, TypedDict, Literal, Callable, Any
from map.abstract import MapStore, Map
from uuid import uuid4

views = Literal["select_map", "create_map", "delete_map"]
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
        self.layout.addWidget(QtWidgets.QLabel("Loading ...", alignment=QtCore.Qt.AlignCenter))
    
    
    def _create_map(self, map_store: MapStore, name: str):
        if len(name) > 0:
            map_store.create_map(name, f"{uuid4()}.dmap")
            self.change_view("select_map") # TODO: Change to editor

    def _delete_map(self, map: Map, map_store: MapStore):
        map_store.delete_map(map)
        self.change_view("select_map")

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
        create_button.clicked.connect(lambda: self._create_map(map_store, name_input.text()))
        
        # Cancel button 
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.change_view("select_map"))

        button_row.addWidget(cancel_button)
        button_row.addWidget(create_button)

        self.layout.addWidget(label)
        self.layout.addWidget(name_input, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(button_row)

    def open_delete_view(self, map: Map, map_store: MapStore):
        # Change to vertical layout
        self.clear_window()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(10)

        label = QtWidgets.QLabel(f"Are you sure you want to delete: '{map.name}'?")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Horizontal layout for buttons
        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(10)
        button_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Delete button
        delete_button = QtWidgets.QPushButton("Delete")
        delete_button.clicked.connect(lambda: self._delete_map(map, map_store))
        
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
        self.setLayout(self.layout)

        # Left panel
        left_panel = QtWidgets.QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        
        # Title above scroll area
        select_title = QtWidgets.QLabel("Select Map")
        select_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(select_title)

        # Scroll area for options
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_content = QtWidgets.QWidget()
        options_layout = QtWidgets.QVBoxLayout(scroll_content)
        options_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # Add all options
        if len(options) == 0:
            options_layout.addWidget(QtWidgets.QLabel("No maps to list."))
        else:
            for option in options:
                option_row = QtWidgets.QWidget()
                row_layout = QtWidgets.QHBoxLayout(option_row)
                row_layout.setContentsMargins(0, 0, 0, 0)

                option_widget = QtWidgets.QLabel(option["text"], alignment=QtCore.Qt.AlignLeft)
                option_widget.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
                option_widget.setStyleSheet("""
                    QLabel {
                        background: gray;
                        padding: 10px;
                    }
                    QLabel:hover {
                        background: lightgray;
                    }
                """)

                delete_button = QtWidgets.QPushButton("Delete")
                delete_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
                delete_button.clicked.connect(lambda: self.change_view("delete_map", option["id"]))
                delete_button.setFixedWidth(50)

                row_layout.addWidget(option_widget)
                row_layout.addWidget(delete_button)
                options_layout.addWidget(option_row)

        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)

        # Button area
        button_container = QtWidgets.QWidget()
        button_container.setFixedHeight(50)
        button_row = QtWidgets.QHBoxLayout(button_container)
        button_row.setSpacing(10)
        button_row.addStretch()
        button_row.addWidget(QtWidgets.QPushButton("Import"))
        button_row.addWidget(QtWidgets.QPushButton("Export"))
        create_button = QtWidgets.QPushButton("Create")
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
    def change_to_view(self, view_name: views, option: Any = None):
        if view_name == "select_map":
            self.window.open_select_view([ { "id": i, "text": map.name } for i, map in enumerate(self.map_store.list()) ])
        elif view_name == "create_map":
            self.window.open_create_view(self.map_store)
        elif view_name == "delete_map":
            map_to_delete = self.map_store.list(no_refresh=True)[option]
            self.window.open_delete_view(map_to_delete, self.map_store)

    # Open the main window
    def open(self, width: int = 800, height: int = 600):
        self.window.resize(width, height)
        self.window.show()

        # Prompt the user to select maps
        self.change_to_view("select_map")

        # Make python wait for window to close before exiting
        exit(self._app.exec())
