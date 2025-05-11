from operator import concat
from PySide6 import QtWidgets, QtCore, QtGui
from os.path import abspath
from map.entity import Map, Element, MapText
from ui.components.buttons import AddElementButtonWidget, AddTextButtonWidget, StandardButtonWidget
from ui.components.editor import EditorGraphicsView
from ui.components.editor_properties.element import ElementPropertiesWidget
from ui.components.editor_properties.text import TextPropertiesWidget
from ui.components.inputs import StandardDropdownWidget
from ui.view import View


class EditorView(View):
    """The editor view, in which the user can edit and view a specific map.
    """

    def _create_element(self, map: Map, x: int, y: int):
        """Private method called when a new element is to be created in a specific location.

        Args:
            map (Map): The map to create the element in.
            x (int): The X coordinate of the element to be created (1/256)
            y (int): The Y coordinate of the element to be created (1/256)
        """
        map.create_element({
            "name": "Unnamed Tile",
            "x": x,
            "y": y,
            "width": 1,
            "height": 1,
            "rotation": 0,
            "background_image": None,
            "background_color": None
        })

    def _create_text(self, map: Map, x: int, y: int):
        """Private method called when a new text object is to be created on a specific map.

        Args:
            map (Map): The map to create the text object in.
            x (int): The X coordinate of the text to be created (true)
            y (int): The Y coordinate of the text to be created (true)
        """
        map.create_text("Unnamed Text", "Text", x, y)

    def _move_element(self, map: Map, id: int, x: int, y: int):
        """Private method called when a specific element is to be moved to a new location in a specific map.

        Args:
            map (Map): The map in which to move a specific element.
            id (int): The id of the element to move.
            x (int): The new X coordinate of the element (1/256)
            y (int): The new Y coordinate of the element (1/256)
        """
        edited_element = map.get_element(id).to_dict()
        edited_element["x"] = x
        edited_element["y"] = y
        map.edit_element(id, edited_element)

    def _move_text(self, map: Map, id: int, x: int, y: int):
        """Private method called when a specific text object is to be moved to a new location in a specific map.

        Args:
            map (Map): The map in which to move the text object.
            id (int): The id of the text object to move.
            x (int): The new X coordinate of the text object (true)
            y (int): The new Y coordinate of the text object (true)
        """
        edited_text = map.get_text(id).to_dict()
        edited_text["x"] = x
        edited_text["y"] = y
        map.edit_text(id, edited_text)

    def _insert_element(self, map: Map, element: Element):
        """Private method called when a specific element should be inserted to the map.

        Args:
            map (Map): The map to which insert the element.
            element (Element): The element to insert.
        """

        element_to_insert = element.to_dict()
        del element_to_insert["id"]
        map.create_element(element_to_insert)

    def _insert_text(self, map: Map, text: MapText):
        """Private method called when a specific text should be inserted to the map.

        Args:
            map (Map): The map to which insert the text.
            text (MapText): The text to insert.
        """

        text_to_insert = text.to_dict()
        # FIXME: Refactor of object handling will unify this with insert_element,
        #        but for now we must create a dummy text object and then edit it
        #        to add all attributes to it.
        created_text = map.create_text(
            "", "", text_to_insert["x"], text_to_insert["y"])
        text_to_insert["id"] = created_text.id
        map.edit_text(created_text.id, text_to_insert)

    def open(self):
        # Change to vertical layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Get target map
        map = self.context.map
        if not map:
            print("ERROR: Editor required target map!")
            return

        # Create top row
        top_bar = QtWidgets.QWidget()
        top_bar.setObjectName("top_bar")
        top_bar.setStyleSheet("""
            #top_bar {
                background-color: #686868;
                border-bottom: 1px solid #5C5C5C; 
            }                                      
        """)
        top_bar.setFixedHeight(32)
        top_bar_layout = QtWidgets.QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(5, 3, 5, 3)
        top_bar_layout.setSpacing(5)

        # Map icon
        map_icon_label = QtWidgets.QLabel()
        map_icon = QtGui.QPixmap(abspath("./ui/icons/map.svg"))
        map_icon_label.setPixmap(map_icon.scaled(
            24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        map_icon_label.setFixedSize(24, 24)

        # Map name on the left
        map_name = QtWidgets.QLabel(f"Map: {map.name if len(map.name) < 32 else map.name[:32] + '...'}")
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
        top_bar_layout.addWidget(map_icon_label)
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

        # View mode dropdown
        view_mode_dropdown = StandardDropdownWidget(
            options=["Editor", "Viewer"])

        # Add buttons
        add_element = AddElementButtonWidget()
        add_text = AddTextButtonWidget()
        toolbar_layout.addWidget(add_element)
        toolbar_layout.addWidget(add_text)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(view_mode_dropdown)

        # Create main editor area (100% <-> x split)
        main = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Actual editor area
        editor_area = EditorGraphicsView()
        view_mode_dropdown.currentIndexChanged.connect(
            lambda index: editor_area.set_preview(index == 1))
        main_layout.addWidget(editor_area)

        # Element Properties side bar
        element_properties_sidebar = ElementPropertiesWidget()
        editor_area.focusObjectEvent.connect(
            lambda: element_properties_sidebar.setAssets(map.get_assets())
        )
        editor_area.focusObjectEvent.connect(
            lambda event: (
                element_properties_sidebar.setElement(
                    map.get_element(event.id))
                if event.id != None and event.type == "element" else
                element_properties_sidebar.setElement(None)
            )
        )
        element_properties_sidebar.editElementEvent.connect(
            lambda event: map.edit_element(event.id, event.element_editable)
        )
        element_properties_sidebar.removeElementEvent.connect(
            lambda event: map.remove_element(event.id)
        )
        main_layout.addWidget(element_properties_sidebar)

        # Text Properties side bar
        text_properties_sidebar = TextPropertiesWidget()
        editor_area.focusObjectEvent.connect(
            lambda event: (
                text_properties_sidebar.setText(map.get_text(event.id))
                if event.id != None and event.type == "text" else
                text_properties_sidebar.setText(None)
            )
        )
        text_properties_sidebar.editTextEvent.connect(
            lambda event: map.edit_text(event.id, event.text_editable)
        )
        text_properties_sidebar.removeTextEvent.connect(
            lambda event: map.remove_text(event.id)
        )
        main_layout.addWidget(text_properties_sidebar)

        # MARK: Editor events
        # Handle editor events
        editor_area.addElementEvent.connect(
            lambda event: self._create_element(map, event.x, event.y))
        editor_area.moveElementEvent.connect(
            lambda event: self._move_element(map, event.id, event.x, event.y))
        editor_area.addTextEvent.connect(
            lambda event: self._create_text(map, event.x, event.y))
        editor_area.moveTextEvent.connect(
            lambda event: self._move_text(map, event.id, event.x, event.y))
        editor_area.pasteElementEvent.connect(
            lambda element: self._insert_element(map, element))
        editor_area.pasteTextEvent.connect(
            lambda text: self._insert_text(map, text))
        editor_area.removeElementEvent.connect(
            lambda element_id: map.remove_element(
                element_id) and element_properties_sidebar.setElement(None)
        )
        editor_area.removeTextEvent.connect(
            lambda text_id: map.remove_text(
                text_id) and text_properties_sidebar.setText(None)
        )

        # When elements change, this is ran
        def render_lambda():
            editor_area.render(concat(map.get_elements(),
                                      map.get_text_list()))

        map.register_on_change(render_lambda)

        # Initial render
        render_lambda()

        self.layout.addWidget(top_bar)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(main)
