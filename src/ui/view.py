from dataclasses import dataclass, field
from typing import Any, Callable, List, Literal, Optional
from PySide6 import QtWidgets
from map.entity import Map
from map_store.store import MapStore


@dataclass
class ViewContext:
    map: Optional[Map] = None
    map_store: Optional[MapStore] = None
    parameters: List[Any] = field(default_factory=list)


Views = Literal["select_map", "create_map",
                "delete_map", "edit_map", "rename_map"]
Changer = Callable[[Views, Any], None]


class View:
    """Simple representation of a view in the application window inside the BaseWindow widget.

    Attributes:
        context (ViewContext): Information passed from the application to the view.
        layout (QtWidgets.QVBoxLayout | QtWidgets.QHBoxLayout | None): The layout of the view.
        view_changer (Changer | None): A reference to a method inside the application to change views.
    """
    context: ViewContext
    layout: QtWidgets.QVBoxLayout | QtWidgets.QHBoxLayout | None
    view_changer: Changer | None

    def __init__(self, context: ViewContext, change_view: Changer):
        """Constructor of the view class.

        Args:
            context (ViewContext): Context to be passed to to the view.
            change_view (Changer): Method for view changing.
        """
        self.context = context
        self.view_changer = change_view

    def change_view(self, view, params=()):
        self.view_changer(view, params)

    # Open the view
    def open(self):
        """Method called when the view is to be opened.
        """
        pass

    # Close the view
    def close(self):
        """Method called when the view is to be closed.
        """
        pass
