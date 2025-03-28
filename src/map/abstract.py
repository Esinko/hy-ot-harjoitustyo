from pathlib import Path
from typing import List, Tuple, Any, TypedDict
from sqlite3 import Connection, connect, Cursor
from map.sql import sql_table

# Init and schema for maps
schema_file = Path("./map/schema.sql")
init_file = Path("./map/init.sql")

if not init_file.exists() or not schema_file.exists():
    raise Exception("Map init or schema missing!")

# Standard asset in the map
class Asset:
    id: int
    name: str
    data: bytes

    def __init__(self, id: int, name: str, data: bytes):
        self.id = id
        self.name = name
        self.data = data

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

    def __init__(self, id: int, name: str, x: int, y: int, width: int, height: int, background_image_id: int | None, background_image_name: int | None, background_image_data: bytes | None, background_color: str | None):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.background_image = Asset(background_image_id, background_image_name, background_image_data) if self.background_image else None
        self.background_color = background_color

class ElementEditable(TypedDict):
    name: str
    x: int
    y: int
    width: int
    height: int
    background_image: Asset | None
    background_color: str | None

# A single map
class Map:
    name: str | None
    map_file: Path
    elements: List[Element]
    _connection: Connection | None

    def __init__(self, map_file: Path, connection: Connection | None = None):
        self.map_file = map_file
        self.name = None
        self.elements = []
        self._connection = connection
        pass

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    # Utility for executing commands against the map
    def _execute(self, query: str, parameters: Tuple[Any] | dict) -> Tuple[Connection, Cursor]:
        if not self._connection:
            raise Exception("Map not open!")
        cursor = self._connection.cursor()
        cursor.execute(query, parameters)
        self._connection.commit()
        return self._connection, cursor
    
    # Utility for querying the map
    def _query(self, query = str, parameters: Tuple[Any] | dict = {}, limit: int = -1) -> list[Any]:
        if not self._connection:
            raise Exception("Map not open!")
        cursor = self._connection.cursor()
        cursor.execute(query, parameters)
        results = cursor.fetchmany(limit)
        cursor.close()
        return results

    # Open the map file
    def open(self):
        # Make sure we can open the map
        if not self.map_file or not self.map_file.exists():
            raise Exception("Map file missing or location uninitialized.")
        if self._connection:
            raise Exception("Map already open.")
        
        self._connection = connect(self.map_file)

        # Read the name of the map
        [result] = self._query(query=sql_table["get_name"])
        if not result:
            raise Exception("Unable to read map Meta table.")
        self.name = result[0]

    # Set the map name
    def set_name(self, name: str) -> str:
        self._execute(query=sql_table["set_name"], parameters=(name,))
        self.name = name
        return name
    
    # Get all the elements
    def get_elements(self) -> List[Element]:
        elements_raw = self._query(query=sql_table["get_elements"])
        return [ Element(*result) for result in elements_raw ]
    
    # Create an element on the map
    def create_element(self, element_editable: ElementEditable) -> Element:
        pass
    
    # Edit an element on the map
    def edit_element(self, element_id: int, element_editable: ElementEditable) -> Element:
        pass

# Manage maps in a folder (a store)
class MapStore:
    store_folder: Path
    _maps: List[Map]

    def __init__(self, path: str):
        self.store_folder = Path(path)
        self._maps = []

        # Check that the store exists
        # and that it is a directory
        if not self.store_folder.exists():
            self.store_folder.mkdir()
        elif self.store_folder.exists() and not self.store_folder.is_dir():
            raise Exception("Store location must be a directory.")

    # Get all the maps in the store
    def list(self, no_refresh: bool = False) -> List[Map]:
        # If we just want to get the list without checking the folder
        if no_refresh:
            return self._maps

        # Close old connections
        for map in self._maps:
            map.close()

        # Get all maps
        self._maps = []
        for map_file in self.store_folder.iterdir():
            if map_file.is_file() and map_file.name.endswith(".dmap"):
                # Attempt to create map
                try:
                    map = Map(map_file)
                    map.open()
                    self._maps.append(map)
                except Exception:
                    # TODO: We discard exceptions for now. Should we log a warning?
                    pass

        return self._maps
    
    # Create a new map
    def create_map(self, name: str, filename: str) -> Map:
        # Make sure file-ending is right
        if not filename.endswith(".dmap"):
            filename = f"{filename}.dmap"

        # Make sure file does not exist
        new_map_file = self.store_folder / filename
        if new_map_file.exists():
            raise Exception("Map already exists.")
        
        # Create the file
        schema = schema_file.read_text()
        connection = connect(new_map_file)
        connection.executescript(schema)

        # Do the db init too
        init = init_file.read_text()
        connection.executescript(init)

        # Create map and set name
        new_map = Map(new_map_file, connection)
        new_map.set_name(name)
    
        # Commit to be done
        connection.commit()
        
        return new_map
    