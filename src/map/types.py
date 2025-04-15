from typing import List, TypedDict


class AssetEditable(TypedDict):
    id: int | None
    name: str
    data: List[int]


class Asset:  # MARK: Asset
    id: int
    name: str
    data: bytes

    def __init__(self, map_id: int, name: str, data: bytes):
        self.id = map_id
        self.name = name
        self.data = data

    def to_dict(self) -> AssetEditable:
        return {
            "id": self.id,
            "name": self.name or "",
            "data": list(self.data) if self.data else []
        }


class AssetNotFoundException(Exception):
    def __init__(self, asset_id):
        super().__init__(f"Asset for id '{asset_id}' not found.")


class ElementEditable(TypedDict):
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
    id: int
    type = "element"
    name: str | None
    x: int
    y: int
    width: int
    height: int
    background_image: Asset | None
    background_color: str | None
    rotation: int

    def __init__(self,
                 element_id: int,
                 name: str,
                 x: int,
                 y: int,
                 width: int,
                 height: int,
                 rotation: int,
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
        self.rotation = rotation

    def to_dict(self) -> ElementEditable:
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
    def __init__(self, element_id):
        super().__init__(f"Element for id '{element_id}' not found.")


class MapMetadataMalformedException(Exception):
    def __init__(self, map_file):
        super().__init__(
            f"Metadata of '{map_file}' is malformed. Cannot read map.")

class TextNotFoundException(Exception):
    def __init__(self, text_id):
        super().__init__(f"Text for id '{text_id}' not found.")

class TextEditable(TypedDict):
    id: int
    name: str | None
    value: str | None
    color: str
    font_size: int
    x: int
    y: int
    rotation: int

class MapText:
    id: int
    type = "text"
    name: str | None
    value: str | None
    color: str
    font_size: int
    x: int
    y: int
    rotation: int

    def __init__(self, id, name, value, color, font_size, x, y, rotation):
        self.id = id
        self.name = name
        self.value = value
        self.color = color
        self.font_size = font_size
        self.x = x
        self.y = y
        self.rotation = rotation

    def to_dict(self) -> TextEditable:
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
    