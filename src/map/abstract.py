from pathlib import Path
from typing import List, Tuple, Any
from os.path import join
from types import FunctionType
from sqlite3 import Connection, connect, Cursor
from traceback import print_exception
from map.sql import sql_table
from map.types import (
    Element,
    Asset,
    ElementEditable,
    ElementNotFoundException,
    MapMetadataMalformedException,
    AssetNotFoundException,
    MapText,
    TextEditable,
    TextNotFoundException
)


class Map:  # MARK: Map
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

    # Close map from editing
    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    # Delete the map itself
    def delete(self):
        self.close()
        self.map_file.unlink()

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

    # Call on_change listener
    def _did_change(self):
        if self._on_change:
            self._on_change()

    # Open the map file
    def open(self):
        # Make sure we can open the map
        if not self.map_file or not self.map_file.exists():
            raise FileNotFoundError(
                "Map file missing or location uninitialized.")
        if self._connection:
            raise ValueError("Map already open.")

        self._connection = connect(self.map_file)

        # Read the name of the map
        [result], _ = self._query(query=sql_table["get_name"], limit=1)
        if not result:
            raise MapMetadataMalformedException(self.map_file.absolute())
        self.name = result[0]

    # Set the map name
    def set_name(self, name: str) -> str:
        self._execute(query=sql_table["set_name"], parameters=(name,))
        self.name = name
        return name

    # MARK: Map elements
    # Get all the elements
    def get_elements(self) -> List[Element]:
        elements_raw, _ = self._query(query=sql_table["get_elements"])
        return [Element(*result) for result in elements_raw]

    # Get a single element
    def get_element(self, element_id: int) -> Element | None:
        element_raw, _ = self._query(
            query=sql_table["get_element"], parameters=(element_id,))
        return Element(*element_raw[0]) if element_raw else None

    # Create an element on the map
    def create_element(self, element_editable: ElementEditable) -> Element:
        _, element_id = self._execute(query=sql_table["create_element"],
                                      parameters=(element_editable["name"],
                                                  element_editable["x"],
                                                  element_editable["y"],
                                                  element_editable["width"],
                                                  element_editable["height"]))
        created_element = self.get_element(element_id)
        self._did_change()
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

        # NOTE: This is not optimal
        current_element = self.get_element(element_id)

        # If no id is provided for the background image, remove current and create a new asset
        if (element_editable["background_image"] is None or
                "id" not in element_editable["background_image"]):
            if current_element.background_image:
                self.remove_asset(current_element.background_image.id)

        # Create new asset if required
        new_asset = None
        if (element_editable["background_image"] is not None and
                "id" not in element_editable["background_image"]):
            new_asset = self.create_asset(element_editable["background_image"]["name"], bytes(
                element_editable["background_image"]["data"]))

        # Perform edit
        self._execute(query=sql_table["edit_element"],
                      parameters=(element_editable["name"],
                                  element_editable["x"],
                                  element_editable["y"],
                                  element_editable["width"],
                                  element_editable["height"],
                                  element_editable["rotation"],
                                  None if not element_editable["background_image"] else (
                                      element_editable["id"] if not new_asset else new_asset.id
                      ),
            element_editable["background_color"],
            element_id))
        self._did_change()
        # NOTE: Id can be changed, technically
        return self.get_element(element_editable["id"])

    # Remove an element
    def remove_element(self, element_id: int):
        if not self.element_exists(element_id):
            raise ElementNotFoundException(element_id)
        self._execute(
            query=sql_table["remove_element"], parameters=(element_id,))
        self._did_change()

    # Create a new asset
    # MARK: Map assets
    def create_asset(self, name: str, value: bytes) -> Asset:
        _, asset_id = self._execute(
            query=sql_table["create_asset"], parameters=(name, value))
        return Asset(asset_id, name, value)

    # Check if asset exists
    def asset_exists(self, asset_id: int) -> bool:
        [[result]], _ = self._query(
            query=sql_table["asset_exists"], parameters=(asset_id,))
        return result == 1

    # Remove an asset
    def remove_asset(self, asset_id: int):
        if not self.asset_exists(asset_id):
            raise AssetNotFoundException(asset_id)
        self._execute(query=sql_table["remove_asset"], parameters=(asset_id,))

    # Create text object
    # MARK: Map text
    def create_text(self, name: str, text: str, x: int, y: int) -> MapText:
        _, text_id = self._execute(
            query=sql_table["create_text"], parameters=(name, text, x, y))
        self._did_change()
        return MapText(text_id, name, text, "#000", 36, x, y, 0)

    # Get a single text object
    def get_text(self, text_id: int) -> MapText | None:
        text_raw, _ = self._query(
            query=sql_table["get_text"], parameters=(text_id,))
        return MapText(*text_raw[0]) if text_raw else None

    # Get all text objects
    def get_text_list(self):
        texts_raw, _ = self._query(query=sql_table["get_all_text"])
        return [MapText(*result) for result in texts_raw]

    # Check if a certain text object exists
    def text_exists(self, text_id: int) -> bool:
        [[result]], _ = self._query(
            query=sql_table["text_exists"], parameters=(text_id,))
        return result == 1

    # Edit text object
    def edit_text(self, text_id: int, text_editable: TextEditable) -> MapText:
        # Make sure text exists, if not, create must be used
        if not self.text_exists(text_id):
            raise TextNotFoundException(text_id)

        # Perform edits
        self._execute(query=sql_table["edit_text"],
                      parameters=(text_editable["name"],
                                  text_editable["value"],
                                  text_editable["color"],
                                  text_editable["font_size"],
                                  text_editable["x"],
                                  text_editable["y"],
                                  text_editable["rotation"],
                                  text_id))
        self._did_change()
        # NOTE: Id can be changed, technically
        return self.get_element(text_editable["id"])

    # Remove text
    def remove_text(self, text_id: int):
        if not self.text_exists(text_id):
            raise TextNotFoundException(text_id)
        self._execute(query=sql_table["remove_text"], parameters=(text_id,))
        self._did_change()


class MapStore:  # MARK: MapStore
    store_folder: Path
    _maps: List[Map]
    schema_file: Path
    init_file: Path

    def __init__(self, path: str, init_path: str | None = None, schema_path: str | None = None):
        self.store_folder = Path(path)
        self._maps = []

        # Init and schema for maps
        self.schema_file = Path(
            schema_path if schema_path else "./map/schema.sql")
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
                except Exception as err:  # pylint: disable=broad-exception-caught
                    # If open fails, ignore the map and log a clear error
                    print(
                        f"WARNING: Failed to open map '{map_file.name}' due to an error:")
                    print_exception(type(err), err, err.__traceback__)

        return self._maps

    # Get a single map with the filename
    def get(self, map_filename: str) -> Map | None:
        # Attempt to reuse connection
        for single_map in self._maps:
            if single_map.map_file.name == map_filename:
                return single_map

        # Try to open from store
        map_file = Path(join(self.store_folder, f"./{map_filename}"))
        if map_file.exists():
            # Open and add to list
            opened_map = Map(map_file)
            opened_map.open()
            self._maps.append(opened_map)
            return opened_map

        return None  # Fallback

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
        connection.close()

        return new_map
