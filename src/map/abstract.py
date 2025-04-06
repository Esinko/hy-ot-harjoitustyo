from pathlib import Path
from typing import List, Tuple, Any, TypedDict
from types import FunctionType
from sqlite3 import Connection, connect, Cursor
from traceback import print_exception
from map.sql import sql_table

# Standard asset in the map
class Asset:
    id: int
    name: str
    data: bytes

    def __init__(self, map_id: int, name: str, data: bytes):
        self.id = map_id
        self.name = name
        self.data = data


class ElementEditable(TypedDict):
    id: int
    name: str
    x: int
    y: int
    width: int
    height: int
    background_image: Asset | None
    background_color: str | None

# An element in the grid
class Element:
    id: int
    name: str | None
    x: int
    y: int
    width: int
    height: int
    background_image: Asset | None
    background_color: str | None

    def __init__(self,
                 element_id: int,
                 name: str,
                 x: int,
                 y: int,
                 width: int,
                 height: int,
                 background_image_id: int | None,
                 background_image_name: int | None,
                 background_image_data: bytes | None,
                 background_color: str | None
    ):
        self.id = element_id
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.background_image = Asset(background_image_id,
                                      background_image_name,
                                      background_image_data) if background_image_id else None
        self.background_color = background_color

    def to_dict(self) -> ElementEditable:
        return {
            "id": self.id,
            "name": self.name or "",
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            # TODO: Properly handle these conversions
            "background_image": self.background_image,
            "background_color": self.background_color,
        }

class ElementNotFoundException(Exception):
    def __init__(self, element_id):
        super().__init__(f"Element for id '{element_id}' not found.")

class MapMetadataMalformed(Exception):
    def __init__(self, map_file):
        super().__init__(f"Metadata of '{map_file}' is malformed. Cannot read map.")

# A single map
class Map:
    name: str | None
    map_file: Path
    elements: List[Element]
    _connection: Connection | None
    _on_change: FunctionType | None

    def __init__(self, map_file: Path, connection: Connection | None = None):
        self.map_file = map_file
        self.name = None
        self.elements = []
        self._connection = connection

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def register_on_change(self, listener: FunctionType):
        self._on_change = listener

    # Utility for executing commands against the map
    def _execute(self, query: str, parameters: Tuple[Any] | dict) -> Tuple[Connection, Cursor]:
        if not self._connection:
            raise ValueError("Map not open!")
        cursor = self._connection.cursor()
        cursor.execute(query, parameters)
        self._connection.commit()
        last_inserted_id = cursor.lastrowid
        cursor.close()
        return self._connection, last_inserted_id

    # Utility for querying the map
    def _query(self, query=str, parameters: Tuple[Any] | dict = None, limit: int = -1) -> list[Any]:
        if not self._connection:
            raise ValueError("Map not open!")
        cursor = self._connection.cursor()
        cursor.execute(query, parameters if parameters else {})
        results = cursor.fetchmany(limit)
        last_inserted_id = cursor.lastrowid
        cursor.close()
        return results, last_inserted_id

    # Open the map file
    def open(self):
        # Make sure we can open the map
        if not self.map_file or not self.map_file.exists():
            raise FileNotFoundError("Map file missing or location uninitialized.")
        if self._connection:
            raise ValueError("Map already open.")

        self._connection = connect(self.map_file)

        # Read the name of the map
        [result], _ = self._query(query=sql_table["get_name"], limit=1)
        if not result:
            raise MapMetadataMalformed(self.map_file.absolute())
        self.name = result[0]

    # Set the map name
    def set_name(self, name: str) -> str:
        self._execute(query=sql_table["set_name"], parameters=(name,))
        self.name = name
        return name

    # Get all the elements
    def get_elements(self) -> List[Element]:
        elements_raw, _ = self._query(query=sql_table["get_elements"])
        return [Element(*result) for result in elements_raw]

    def get_element(self, element_id: int) -> Element | None:
        [element_raw], _ = self._query(
            query=sql_table["get_element"], parameters=(element_id,))
        return Element(*element_raw) if element_raw else None

    # Create an element on the map
    def create_element(self, element_editable: ElementEditable) -> Element:
        _, element_id = self._execute(query=sql_table["create_element"],
                                      parameters=(element_editable["name"],
                                                  element_editable["x"],
                                                  element_editable["y"],
                                                  element_editable["width"],
                                                  element_editable["height"]))
        created_element = self.get_element(element_id)
        if self._on_change:
            self._on_change()
        return created_element

    # Check if a element with a given id exists
    def element_exists(self, element_id: int) -> bool:
        [[result]], _ = self._query(
            query=sql_table["element_exists"], parameters=(element_id,))
        return result == 1

    # Edit an element on the map
    def edit_element(self, element_id: int, element_editable: ElementEditable) -> Element:
        # Make sure element exists, otherwise use of create_element is required
        if not self.element_exists(element_id):
            raise ElementNotFoundException(element_id)

        self._execute(query=sql_table["edit_element"],
                      parameters=(element_editable["name"],
                                  element_editable["x"],
                                  element_editable["y"],
                                  element_editable["width"],
                                  element_editable["height"],
                                  element_editable["background_image"].id
                                    if element_editable["background_image"] else None,
                                  element_editable["background_color"],
                                  element_id))
        if self._on_change:
            self._on_change()
        # NOTE: Id can be changed, technically
        return self.get_element(element_editable["id"])


# Manage maps in a folder (a store)
class MapStore:
    store_folder: Path
    _maps: List[Map]
    schema_file: Path
    init_file: Path

    def __init__(self, path: str, init_path: str | None = None, schema_path: str | None = None):
        self.store_folder = Path(path)
        self._maps = []

        # Init and schema for maps
        self.schema_file = Path(schema_path if schema_path else "./map/schema.sql")
        self.init_file = Path(init_path if init_path else "./map/init.sql")

        if not self.init_file.exists() or not self.schema_file.exists():
            raise FileNotFoundError("Map init or schema missing!")

        # Check that the store exists
        # and that it is a directory
        if not self.store_folder.exists():
            self.store_folder.mkdir()
        elif self.store_folder.exists() and not self.store_folder.is_dir():
            raise NotADirectoryError("Store location must be a directory.")

    # Get all the maps in the store
    def list(self, no_refresh: bool = False) -> List[Map]:
        # If we just want to get the list without checking the folder
        if no_refresh:
            return self._maps

        # Close old connections
        for a_map in self._maps:
            a_map.close()

        # Get all maps
        self._maps = []
        for map_file in self.store_folder.iterdir():
            if map_file.is_file() and map_file.name.endswith(".dmap"):
                # Attempt to open map
                try:
                    opened_map = Map(map_file)
                    opened_map.open()
                    self._maps.append(opened_map)
                except Exception as err: # pylint: disable=broad-exception-caught
                    # If open fails, ignore the map and log a clear error
                    print(f"WARNING: Failed to open map '{map_file.name}' due to an error:")
                    print_exception(type(err), err, err.__traceback__)

        return self._maps

    # Close the store
    def close(self):
        # Close old connections
        for a_map in self._maps:
            a_map.close()

    # Create a new map
    def create_map(self, name: str, filename: str) -> Map:
        # Make sure file-ending is right
        if not filename.endswith(".dmap"):
            filename = f"{filename}.dmap"

        # Make sure file does not exist
        new_map_file = self.store_folder / filename
        if new_map_file.exists():
            raise FileExistsError("Map already exists!")

        # Create the file
        schema = self.schema_file.read_text("utf8")
        connection = connect(new_map_file)
        connection.executescript(schema)

        # Do the db init too
        init = self.init_file.read_text("utf8")
        connection.executescript(init)

        # Create map and set name
        new_map = Map(new_map_file, connection)
        new_map.set_name(name)

        # Commit to be done
        connection.commit()

        return new_map

    # Delete a map
    def delete_map(self, target_map: Map):
        target_map.close()
        target_map.map_file.unlink()
