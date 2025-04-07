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
            "data": list(self.data)
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
    background_image: AssetEditable | None
    background_color: str | None


class Element:  # MARK: Element
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
            "background_image": self.background_image.to_dict() if self.background_image else None,
            "background_color": self.background_color,
        }


class ElementNotFoundException(Exception):
    def __init__(self, element_id):
        super().__init__(f"Element for id '{element_id}' not found.")


class MapMetadataMalformedException(Exception):
    def __init__(self, map_file):
        super().__init__(
            f"Metadata of '{map_file}' is malformed. Cannot read map.")
