from dataclasses import dataclass, field
from typing import Any, Callable, List, Literal, Optional
from PySide6 import QtWidgets
from map.abstract import Map, MapStore

@dataclass
class ViewContext:
    map: Optional[Map] = None
    map_store: Optional[MapStore] = None
    parameters: List[Any] = field(default_factory=list)

Views = Literal["select_map", "create_map",
                "delete_map", "edit_map", "rename_map"]
Changer = Callable[[Views, Any], None]

class View:
    context: ViewContext
    layout: QtWidgets.QVBoxLayout | QtWidgets.QHBoxLayout | None
    view_changer: Changer | None

    def __init__(self, context: ViewContext, change_view: Changer):
        self.context = context
        self.view_changer = change_view

    def change_view(self, view, params = ()):
        self.view_changer(view, params)

    # Open the view
    def open(self):
        pass
    
    # Close the view
    def close(self):
        pass
    