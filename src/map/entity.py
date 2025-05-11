from pathlib import Path
from typing import List, Tuple, Any
from types import FunctionType, MethodType
from sqlite3 import Connection, connect, Cursor
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
    TextNotFoundException,
    MapOutdatedException
)


CURRENT_MAP_VERSION = 2


class Map:  # MARK: Map
    """A single map and methods to control it.

    Attributes:
        name (str): The maps name.
        version (int): The map file version.
        map_file (Path): The Path instance of the map's location on disk.
        elements (List[Element]): List of elements on the map.
        _connection (Connection | None): SQLite3 connection of the map.
        _on_change (MethodType | None): A method, when defined, called when the map is modified.
    """
    name: str | None
    version: int | None
    map_file: Path
    elements: List[Element]
    _connection: Connection | None
    _on_change: MethodType | None

    def __init__(self, map_file: Path, connection: Connection | None = None):
        """Constructor of the map class.

        Args:
            map_file (Path): The Path instance of the map on the disk.
            connection (Connection | None, optional): A connection to be re-used. Defaults to None.
        """
        self.map_file = map_file
        self.name = None
        self.elements = []
        self._connection = connection
        self._on_change = None

    def close(self):
        """Close the map when done with it.
        """
        if self._connection:
            self._connection.close()
            self._connection = None

    def delete(self):
        """Delete this map
        """
        self.close()
        self.map_file.unlink()

    def register_on_change(self, listener: FunctionType):
        """Register a method as the on_change method. Can be called many times.

        Args:
            listener (FunctionType): Method called when changes happen.
        """
        self._on_change = listener

    # Utility for executing commands against the map
    def _execute(self, query: str, parameters: Tuple[Any] | dict) -> Tuple[Connection, Cursor]:
        """Execute a SQL command against the map database.

        Args:
            query (str): The SQL to execute
            parameters (Tuple[Any] | dict): Parameters for the SQL

        Raises:
            ValueError: Map is not yet open.

        Returns:
            Tuple[Connection, Cursor]: Current map connection and the last inserted row id.
        """
        if not self._connection:
            raise ValueError("Map not open!")
        cursor = self._connection.cursor()
        cursor.execute(query, parameters)
        self._connection.commit()
        last_inserted_id = cursor.lastrowid
        cursor.close()
        return self._connection, last_inserted_id

    # Utility for querying the map
    def _query(self, query="", parameters: Tuple[Any] | dict = None, limit: int = -1) -> list[Any]:
        """Issue a SQL query against the map database.

        Args:
            query (_type_, optional): The query to execute.
            parameters (Tuple[Any] | dict, optional): Parameters for the query. Defaults to None.
            limit (int, optional): Number of rows to fetch. Defaults to -1.

        Raises:
            ValueError: Map is not open.

        Returns:
            list[Any]: List of rows in SQLite3 lib form.
        """
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
        """Called internally to trigger the on_change method, if defined.
        """
        if self._on_change:
            self._on_change()

    # Open the map file
    def open(self):
        """Open the map for reading and modifications.

        Raises:
            FileNotFoundError: The path of the map file is invalid
            ValueError: The map is already open
            MapMetadataMalformedException: The map's data is malformed and it cannot be opened
            MapOutdatedException: The map is outdated, version too low or not present
        """
        # Make sure we can open the map
        if not self.map_file or not self.map_file.exists():
            raise FileNotFoundError(
                "Map file missing or location uninitialized.")
        if self._connection:
            raise ValueError("Map already open.")

        self._connection = connect(self.map_file)

        # Check that meta contains required version
        # Some old map files don't have it
        [[column_count]], _ = self._query(
            query=sql_table["get_meta_size"], limit=1)
        if not column_count or column_count < 3:
            raise MapOutdatedException(self.map_file.absolute())

        # Read the name of the map
        [meta], _ = self._query(query=sql_table["get_meta"], limit=1)
        if not meta:
            raise MapMetadataMalformedException(self.map_file.absolute())

        # Detect outdated version
        if meta[0] < CURRENT_MAP_VERSION:
            raise MapOutdatedException(self.map_file.absolute())

        self.name = meta[1]
        self.version = meta[0]

    # Set the map name
    def set_name(self, name: str) -> str:
        """Set the name of the map.

        Args:
            name (str): The new name.

        Returns:
            str: The name that was set.
        """
        self._execute(query=sql_table["set_name"], parameters=(name,))
        self.name = name
        return name

    # MARK: Map elements
    # Get all the elements
    def get_elements(self) -> List[Element]:
        """Get all the elements on the map.

        Returns:
            List[Element]: List of elements on the map.
        """
        elements_raw, _ = self._query(query=sql_table["get_elements"])
        return [Element(*result) for result in elements_raw]

    # Get a single element
    def get_element(self, element_id: int) -> Element | None:
        """Get an element by id.

        Args:
            element_id (int): The id of the element.

        Returns:
            Element | None: The element or none, if not found.
        """
        element_raw, _ = self._query(
            query=sql_table["get_element"], parameters=(element_id,))
        return Element(*element_raw[0]) if element_raw else None

    # Create an element on the map
    def create_element(self, element_editable: ElementEditable) -> Element:
        """Create a new element on the map.

        Args:
            element_editable (ElementEditable): Details of the new element's form.

        Returns:
            Element: The created element.
        """
        # If background is present, create asset
        new_asset_id = None
        if "background_image" in element_editable and element_editable["background_image"]:
            new_asset = self.create_asset(element_editable["background_image"]["name"],
                                          bytes(element_editable["background_image"]["data"]))
            new_asset_id = new_asset.id

        _, element_id = self._execute(query=sql_table["create_element"],
                                      parameters=(element_editable["name"],
                                                  element_editable["x"],
                                                  element_editable["y"],
                                                  element_editable["width"],
                                                  element_editable["height"],
                                                  new_asset_id))
        created_element = self.get_element(element_id)
        self._did_change()
        return created_element

    # Check if a element with a given id exists
    def element_exists(self, element_id: int) -> bool:
        """Check if an element exists by id

        Args:
            element_id (int): The id to check

        Returns:
            bool: True when element exists.
        """
        [[result]], _ = self._query(
            query=sql_table["element_exists"], parameters=(element_id,))
        return result == 1

    # Edit an element on the map
    def edit_element(self, element_id: int, element_editable: ElementEditable) -> Element:
        """Edit an element on the map by id.

        Args:
            element_id (int): The id of the element to edit.
            element_editable (ElementEditable): The new details of the elements form.

        Raises:
            ElementNotFoundException: The element to edit was not found.

        Returns:
            Element: The edited element
        """
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
        if (element_editable["background_image"] and
                "id" not in element_editable["background_image"]):
            new_asset = self.create_asset(element_editable["background_image"]["name"], bytes(
                element_editable["background_image"]["data"]))

        # Perform edit
        background_value = None
        if new_asset:
            background_value = new_asset.id
        elif element_editable["background_image"] and "id" in element_editable["background_image"]:
            background_value = element_editable["background_image"]["id"]

        self._execute(query=sql_table["edit_element"],
                      parameters=(element_editable["name"],
                                  element_editable["x"],
                                  element_editable["y"],
                                  element_editable["width"],
                                  element_editable["height"],
                                  element_editable["rotation"],
                                  background_value,
                                  element_editable["background_color"],
                                  element_id
                                  ))
        self._did_change()
        # NOTE: Id can be changed, technically
        return self.get_element(element_editable["id"])

    # Remove an element
    def remove_element(self, element_id: int):
        """Remove an element from the map by id.

        Args:
            element_id (int): The id of the element to be removed.

        Raises:
            ElementNotFoundException: The element was not found.
        """
        if not self.element_exists(element_id):
            raise ElementNotFoundException(element_id)
        self._execute(
            query=sql_table["remove_element"], parameters=(element_id,))
        self._did_change()

    # Create a new asset
    # MARK: Map assets
    def create_asset(self, name: str, value: bytes) -> Asset:
        """Create a new asset in the map database.

        Args:
            name (str): Name of the new asset.
            value (bytes): The raw bytes of the asset.

        Returns:
            Asset: The created asset.
        """
        _, asset_id = self._execute(
            query=sql_table["create_asset"], parameters=(name, value))
        return Asset(asset_id, name, value)

    # Check if asset exists
    def asset_exists(self, asset_id: int) -> bool:
        """Check that an asset exists by id.

        Args:
            asset_id (int): The id of the asset to check.

        Returns:
            bool: True when the asset exists.
        """
        [[result]], _ = self._query(
            query=sql_table["asset_exists"], parameters=(asset_id,))
        return result == 1

    def get_assets(self) -> List[Asset]:
        """Get an assets stored in the map.

        Returns:
            List[Asset]: The assets.
        """

        assets, _ = self._query(
            query=sql_table["get_assets"])
        return list(Asset(*asset_raw) for asset_raw in assets)

    # Remove an asset
    def remove_asset(self, asset_id: int):
        """Remove an asset from the map database.

        Args:
            asset_id (int): The id of the asset to remove.

        Raises:
            AssetNotFoundException: The asset was not found.
        """
        if not self.asset_exists(asset_id):
            raise AssetNotFoundException(asset_id)
        self._execute(query=sql_table["remove_asset"], parameters=(asset_id,))

    # Create text object
    # MARK: Map text
    def create_text(self, name: str, text: str, x: int, y: int) -> MapText:
        """Create a text object on the map

        Args:
            name (str): The name of the text object.
            text (str): The text inside the text object.
            x (int): X coordinate (true).
            y (int): Y coordinate (true).

        Returns:
            MapText: The created text.
        """
        _, text_id = self._execute(
            query=sql_table["create_text"], parameters=(name, text, x, y))
        self._did_change()
        return MapText(text_id, name, text, "#000", 36, x, y, 0)

    # Get a single text object
    def get_text(self, text_id: int) -> MapText | None:
        """Get text object by id.

        Args:
            text_id (int): The id of the text.

        Returns:
            MapText | None: The text object or None if not found.
        """
        text_raw, _ = self._query(
            query=sql_table["get_text"], parameters=(text_id,))
        return MapText(*text_raw[0]) if text_raw else None

    # Get all text objects
    def get_text_list(self):
        """Get list of all text objects on the map.

        Returns:
            List[MapText]: List of text objects.
        """
        texts_raw, _ = self._query(query=sql_table["get_all_text"])
        return [MapText(*result) for result in texts_raw]

    # Check if a certain text object exists
    def text_exists(self, text_id: int) -> bool:
        """Check that a text object exits on the map by id.

        Args:
            text_id (int): The id of the text object.

        Returns:
            bool: True when the text object exists.
        """
        [[result]], _ = self._query(
            query=sql_table["text_exists"], parameters=(text_id,))
        return result == 1

    # Edit text object
    def edit_text(self, text_id: int, text_editable: TextEditable) -> MapText:
        """Edit a text object on the map.

        Args:
            text_id (int): The id of the text object to edit.
            text_editable (TextEditable): The details of the text objects new form.

        Raises:
            TextNotFoundException: The text object was not found.

        Returns:
            MapText: The edited text object.
        """
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
        """Remove a text object from the map.

        Args:
            text_id (int): The id of the text to be removed.

        Raises:
            TextNotFoundException: The text object was not found.
        """
        if not self.text_exists(text_id):
            raise TextNotFoundException(text_id)
        self._execute(query=sql_table["remove_text"], parameters=(text_id,))
        self._did_change()
