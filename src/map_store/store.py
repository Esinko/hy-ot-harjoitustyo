from pathlib import Path
from typing import List
from os.path import join
from sqlite3 import connect
from traceback import print_exception
from uuid import uuid4
from map.entity import Map
from map.types import (
    InvalidPathException,
    MapMetadataMalformedException,
)


class MapStore:  # MARK: MapStore
    """Used to manage maps in a central store.

    Attributes:
        store_folder (Path): The location of the map store.
        _maps (List[Map]): Cache of maps in the sore.
        schema_file (Path): Path to the map schema.
        init_file (Path): Path to the map init SQL.
    """
    store_folder: Path
    _maps: List[Map]
    schema_file: Path
    init_file: Path

    def __init__(self, path: str, init_path: str | None = None, schema_path: str | None = None):
        """Constructor of the map store class.

        Args:
            path (str): Path of the map store
            init_path (str | None): Path of the map init file.
            schema_path (str | None): Path of the map schema file.

        Raises:
            FileNotFoundError: The init or schema file is missing
            NotADirectoryError: The given store folder path is not a directory.
        """
        self.store_folder = Path(path)
        self._maps = []

        # Init and schema for maps
        self.schema_file = Path(
            schema_path if schema_path else "./map_store/schema.sql")
        self.init_file = Path(
            init_path if init_path else "./map_store/init.sql")

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
        """List all the maps in the map store.

        Args:
            no_refresh (bool, optional): If to use the cache or not. Defaults to False.

        Returns:
            List[Map]: A list of maps in the map store.
        """
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
        """Get a map from the store with it's filename (id).

        Args:
            map_filename (str): The map's filename.

        Returns:
            Map | None: The map from the store or None when not found.
        """
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

    # Export a map to a specific location
    def export(self, map_to_export: Map, location: str):
        """Export a map from the store to some location (copy action)

        Args:
            map (Map): The map to export.
            location (str): The location to export to.

        Raises:
            InvalidPathException: The given path to export to is invalid.
        """
        try:
            target_location = Path(location)
        except TypeError as type_err:
            raise InvalidPathException(location) from type_err

        # Copy map to target
        target_location.write_bytes(map_to_export.map_file.read_bytes())

    # Add a map to the map store from a specified location
    def add(self, location: str) -> Map | None:
        """Add a map to the store from a specified location (copy action)

        Args:
            location (str): The location of the map to add to the store.

        Raises:
            InvalidPathException: The given path was invalid.

        Returns:
            Map | None: The added map or None if not possible.
        """
        try:
            map_file = Path(location)
        except TypeError as type_err:
            raise InvalidPathException(location) from type_err

        # Try to load the map
        try:
            loaded_map = Map(map_file)
            loaded_map.open()
            loaded_map.close()
        except MapMetadataMalformedException:
            print("ERROR: Map to be loaded is invalid!")
            return None

        # Copy map to store
        map_location = self.store_folder.absolute() / f"{uuid4()}.dmap"
        map_copy = Path(map_location)
        map_copy.write_bytes(map_file.read_bytes())

        return Map(map_copy)

    # Close the store
    def close(self):
        """Close the map store's map database connections.
        """
        # Close old connections
        for a_map in self._maps:
            a_map.close()

    # Create a new map
    def create_map(self, name: str, filename: str) -> Map:
        """Create a new map in the map store.

        Args:
            name (str): The name of the new map.
            filename (str): The filename of the new map (id)

        Raises:
            FileExistsError: The map already exists.

        Returns:
            Map: The created map.
        """
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
        self._maps.append(new_map)

        return new_map
