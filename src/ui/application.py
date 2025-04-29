from PySide6 import QtCore, QtWidgets
from sys import exit
from typing import List, TypedDict,  Any
from map.entity import Map
from map_store.store import MapStore
from ui.view import Changer, View, ViewContext, Views
from ui.views.create import CreateView
from ui.views.delete import DeleteView
from ui.views.editor import EditorView
from ui.views.rename import RenameView
from ui.views.select import SelectView


class SelectOption(TypedDict):
    id: str
    text: str

# TODO: Refactor BaseWindow and application as a combined ApplicationWindow class


class BaseWindow(QtWidgets.QWidget):  # MARK: Base window
    """The main widget inside the QT window.

    Attributes:
        change_view (Changer): Method of changing the views inside the application.
        current_view (View | None): The view currently on display. None when empty.
    """
    change_view: Changer
    current_view: View | None

    def __init__(self, change_view: QtCore.Slot):
        """Constructor of the main widget. Styles the widget and adds a loading placeholder.
        """
        super().__init__()
        self.setWindowTitle("Blocky Dungeon Mapper")
        self.change_view = change_view
        self.current_view = None

        # Window style
        self.setObjectName("window")
        self.setStyleSheet("""
            #window {
                background-color: #727272;
            }               
        """)

        # Loading placeholder
        loading_layout = QtWidgets.QVBoxLayout(self)
        loading_layout.addWidget(QtWidgets.QLabel(
            "Loading ...", alignment=QtCore.Qt.AlignCenter))
        self.setLayout(loading_layout)

    def clear_window(self):
        """Method for clearing the contents of the window.
        Primes it for loading a new view.
        """
        old_layout = self.layout()

        # If old layout is present, we need to remove it
        if old_layout:
            present = False
            try:
                # Attempt to get count of items
                # This will raise a RuntimeError if the C++ obj
                # is not present anymore
                old_layout.count()
                present = True
            except RuntimeError:
                pass

            # Loop over all, event nested, widgets, and delete
            while present and old_layout.count():
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
            # This will dereference the layout
            if present:
                QtWidgets.QWidget().setLayout(old_layout)

        # Run view teardown
        if self.current_view:
            self.current_view.close()

    # MARK: Editor view
    def open_editor_view(self, map: Map):
        """Open the editor view inside the window.

        Args:
            map (Map): The map to edit.
        """
        self.clear_window()
        editor_view = EditorView(ViewContext(map=map), self.change_view)
        editor_view.open()
        self.setLayout(editor_view.layout)
        self.current_view = editor_view

    # MARK: Create view
    def open_create_view(self, map_store: MapStore):
        """Open the create new map view inside the window.

        Args:
            map_store (MapStore): The map store to create the new map in.
        """
        self.clear_window()
        # TODO: Can we design this view in a way to not need to use map_store directly?
        create_view = CreateView(ViewContext(map_store=map_store),
                                 self.change_view)
        create_view.open()
        self.setLayout(create_view.layout)
        self.current_view = create_view

    # MARK: Rename view
    def open_rename_view(self, map: Map, to_view: Views):
        """Open the rename view inside the window.

        Args:
            map (Map): _The map to rename.
            to_view (Views): The view to change after renaming or canceling.
        """
        self.clear_window()
        rename_view = RenameView(ViewContext(map=map, parameters=[to_view]),
                                 self.change_view)
        rename_view.open()
        self.setLayout(rename_view.layout)
        self.current_view = rename_view

    # MARK: Delete view
    def open_delete_view(self, map: Map):
        """Open the delete view inside the window.

        Args:
            map (Map): The map to be potentially deleted.
        """
        self.clear_window()
        delete_view = DeleteView(ViewContext(map=map), self.change_view)
        delete_view.open()
        self.setLayout(delete_view.layout)
        self.current_view = delete_view

    # MARK: Select view
    def open_select_view(self, map_store: MapStore, options: List[SelectOption]):
        """Open the select map (list view) view inside the window

        Args:
            map_store (MapStore): Map store to pass to the view
            options (List[SelectOption]): List options to pass to the view
        """
        self.clear_window()
        # TODO: Can we design this view in a way to not use map_store directly and opt for map instead?
        select_view = SelectView(ViewContext(parameters=[options], map_store=map_store),
                                 self.change_view)
        select_view.open()
        self.setLayout(select_view.layout)
        self.current_view = select_view


class Application:  # MARK: Application
    """The main application class

    Attributes:
        _app (QApplication): The QT application reference
        window: The window inside the application, when created
        map_store: The map store to be used by the application
    """
    _app: QtWidgets.QApplication
    window: BaseWindow
    map_store: MapStore

    def __init__(self, map_store: MapStore):
        """The constructor of the application class, which initializes the BaseWindow and QApplication.

        Args:
            map_store (MapStore): The map store to use in the application.
        """
        self._app = QtWidgets.QApplication([])
        self.window = BaseWindow(self.change_to_view)
        self.map_store = map_store

    # TODO: Would it be better to store all the parameters in the BaseWindow class as privates?
    # TODO: Find a way to maintain proper logical separation of map_store and map usage
    def change_to_view(self, view_name: Views, option: Any = None):
        """Change the view inside the window

        Args:
            view_name (Views): The view to change to.
            option (Any, optional): Any view specific parameters. Defaults to None.
        """
        if view_name == "select_map":
            self.window.open_select_view(
                self.map_store,
                [{"id": map.map_file.name, "text": map.name} for map in self.map_store.list()])
        elif view_name == "create_map":
            self.window.open_create_view(self.map_store)
        elif view_name == "delete_map":
            map_to_delete = self.map_store.get(option)
            self.window.open_delete_view(map_to_delete)
        elif view_name == "rename_map":
            self.window.open_rename_view(
                self.map_store.get(option[0]), option[1])
        elif view_name == "edit_map":
            map_to_edit = self.map_store.get(option)
            self.window.open_editor_view(map_to_edit)
        else:
            print(f"Tried to open view '{view_name}', which does not exist.")

    # Open the main window
    def open(self, width: int = 800, height: int = 600):
        """Open the application window.

        Args:
            width (int, optional): The width of the application window. Defaults to 800.
            height (int, optional): The height of the application window. Defaults to 600.
        """
        self.window.resize(width, height)
        self.window.show()

        # Prompt the user to select maps
        self.change_to_view("select_map")

        # Make python wait for window to close before exiting
        exit(self._app.exec())
