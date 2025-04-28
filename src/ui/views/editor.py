from operator import concat
from PySide6 import QtWidgets, QtCore
from map.abstract import Map
from ui.components.buttons import AddElementButtonWidget, AddTextButtonWidget, StandardButtonWidget
from ui.components.editor import EditorGraphicsView
from ui.components.editor_properties.element import ElementPropertiesWidget
from ui.components.editor_properties.text import TextPropertiesWidget
from ui.view import View

class EditorView(View):
    def _create_element(self, map: Map, x: int, y: int):
        map.create_element({
            "name": "Unnamed Tile",
            "x": x,
            "y": y,
            "width": 1,
            "height": 1
        })

    def _create_text(self, map: Map, x: int, y: int):
        map.create_text("Unnamed Text", "Text", x, y)

    def _move_element(self, map: Map, id: int, x: int, y: int):
        edited_element = map.get_element(id).to_dict()
        edited_element["x"] = x
        edited_element["y"] = y
        map.edit_element(id, edited_element)

    def _move_text(self, map: Map, id: int, x: int, y: int):
        edited_text = map.get_text(id).to_dict()
        edited_text["x"] = x
        edited_text["y"] = y
        map.edit_text(id, edited_text)

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

        # Add buttons
        add_element = AddElementButtonWidget()
        add_text = AddTextButtonWidget()
        toolbar_layout.addWidget(add_element)
        toolbar_layout.addWidget(add_text)

        # Create main editor area (100% <-> x split)
        main = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Actual editor area
        editor_area = EditorGraphicsView()

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

        def render_lambda(): return editor_area.render(
            concat(map.get_elements(),
                   map.get_text_list()))
        # When elements change, this is ran
        map.register_on_change(render_lambda)
        main_layout.addWidget(editor_area)

        # Initial render pass for editor
        render_lambda()

        # Element Properties side bar
        element_properties_sidebar = ElementPropertiesWidget()
        editor_area.focusObjectEvent.connect(
            # TODO: Handle different types of objects
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
        text_properties_sidebar.editTextEvent.connect(
            lambda event: map.edit_text(event.id, event.text_editable)
        )
        text_properties_sidebar.removeTextEvent.connect(
            lambda event: map.remove_text(event.id)
        )
        editor_area.focusObjectEvent.connect(
            # TODO: Handle different types of objects
            lambda event: (
                text_properties_sidebar.setText(map.get_text(event.id))
                if event.id != None and event.type == "text" else
                text_properties_sidebar.setText(None)
            )
        )

        main_layout.addWidget(text_properties_sidebar)

        self.layout.addWidget(top_bar)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(main)