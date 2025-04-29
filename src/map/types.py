from typing import List, TypedDict


class AssetEditable(TypedDict):
    """Asset in dict form.
    """
    id: int | None
    name: str
    data: List[int]


class Asset:  # MARK: Asset
    """An asset in the map database.

    Attributes:
        id (int): The ID of the asset.
        name (str): The name of the asset.
        data (bytes): The raw bytes of the asset.
    """
    id: int
    name: str
    data: bytes

    def __init__(self, asset_id: int, name: str, data: bytes):
        """The constructor of the Asset class.

        Args:
            map_id (int): The id of the asset.
            name (str): The name of the asset.
            data (bytes): The raw buts of the asset.
        """
        self.id = asset_id
        self.name = name
        self.data = data

    def to_dict(self) -> AssetEditable:
        """Convert the asset to dict form.

        Returns:
            AssetEditable: The asset in dict form.
        """
        return {
            "id": self.id,
            "name": self.name or "",
            "data": list(self.data) if self.data else []
        }


class AssetNotFoundException(Exception):
    """Exception to be raised when an asset is not found.
    """

    def __init__(self, asset_id):
        """The constructor of the AssetNotFound exception.

        Args:
            asset_id (_type_): The id of the asset not found.
        """
        super().__init__(f"Asset for id '{asset_id}' not found.")


class ElementEditable(TypedDict):
    """Element in dict form.
    """
    id: int
    name: str
    x: int
    y: int
    width: int
    height: int
    rotation: int
    background_image: AssetEditable | None
    background_color: str | None


class Element:  # MARK: Element
    """Class representation of a single element on the map (square, grid element)

    Attributes:
        id (int): The id of the element.
        type (str): The type of the object. Defaults to "element".
        name (str): The name of the element.
        x: (int): The X coordinate of the element (1/256)
        y (int): The Y coordinate of thr element (1/256)
        width (int): The width of the element.
        height (int): The height of the element.
        rotation (int): The rotation of content in the element.
        background_image (Asset | None): The background image of the element.
        background_color: (str | None): The background color of the element.
    """
    id: int
    type = "element"
    name: str | None
    x: int
    y: int
    width: int
    height: int
    rotation: int
    background_image: Asset | None
    background_color: str | None

    def __init__(self, *raw):
        """The constructor of the Element class
        """
        self.id = raw[0]
        self.name = raw[1]
        self.x = raw[2]
        self.y = raw[3]
        self.width = raw[4]
        self.height = raw[5]
        self.background_image = Asset(raw[7],
                                      raw[8],
                                      raw[9]) if raw[7] else None
        self.background_color = raw[9]
        self.rotation = raw[6]

    def to_dict(self) -> ElementEditable:
        """Transform the element to dict form.

        Returns:
            ElementEditable: The element in dict form.
        """
        return {
            "id": self.id,
            "name": self.name or "",
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "background_image": self.background_image.to_dict() if self.background_image else None,
            "background_color": self.background_color,
            "rotation": self.rotation
        }


class ElementNotFoundException(Exception):
    """Exception to be raised when an element was not found.
    """

    def __init__(self, element_id):
        """The constructor of the ElementNotFound exception.

        Args:
            element_id (str | id): The id of the element that was not found. 
        """
        super().__init__(f"Element for id '{element_id}' not found.")


class MapMetadataMalformedException(Exception):
    """Exception to be raised when the map metadata is malformed.
    """

    def __init__(self, map_file):
        """The constructor of the MapMetadataMalformed exception.

        Args:
            map_file (str): The location of the map that is malformed.
        """
        super().__init__(
            f"Metadata of '{map_file}' is malformed. Cannot read map.")


class TextNotFoundException(Exception):
    """Exception to be raised when a text object is not found.
    """

    def __init__(self, text_id):
        """The constructor of the ElementNotFound exception.

        Args:
            text_id (id | str): The id of the the text object that was not found.
        """
        super().__init__(f"Text for id '{text_id}' not found.")


class TextEditable(TypedDict):
    """Text object in dict form.
    """
    id: int
    name: str | None
    value: str | None
    color: str
    font_size: int
    x: int
    y: int
    rotation: int


class InvalidPathException(Exception):
    """Exception to be raised when a given path was invalid.
    """

    def __init__(self, path):
        """The constructor of the InvalidPath exception.

        Args:
            path (str): The invalid path.
        """
        super().__init__(f"Given path '{path}' is invalid.")


class MapText:  # MARK: Text
    """Class representation of a text object on the map.

    Attributes:
        id (int): The id of the text object
        type (str): The type of the object. Defaults to text.
        name (str): The name of the text object.
        value (str): The text inside the object.
        color (str): Hex color of the text.
        font_size (int): Pixel size of the text.
        x (int): X coordinate of the text object (true)
        y (int): Y coordinate of the text (true)
        rotation (int): Rotation of the text object.
    """
    id: int
    type = "text"
    name: str | None
    value: str | None
    color: str
    font_size: int
    x: int
    y: int
    rotation: int

    def __init__(self, *raw):
        """The constructor of the text object class.

        Args:
            text_id (id): The id of the text object.
            name (str): The name of the text object.
            value (str): The text inside the object.
            color (str): Hex color of the text.
            font_size (int): The pixel size of the text.
            x (int): The X coordinate of the text (true)
            y (int): The Y coordinate of the text (true)
            rotation (int): The rotation of the text object.
        """
        self.id = raw[0]
        self.name = raw[1]
        self.value = raw[2]
        self.color = raw[3]
        self.font_size = raw[4]
        self.x = raw[5]
        self.y = raw[6]
        self.rotation = raw[7]

    def to_dict(self) -> TextEditable:
        """Get the text object in dict form.

        Returns:
            TextEditable: The text object in dict form.
        """
        return {
            "id": self.id,
            "name": self.name or "",
            "value": self.value or "",
            "color": self.color or "#000",
            "font_size": self.font_size or 24,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation
        }
