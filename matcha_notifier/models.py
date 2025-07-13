from dataclasses import dataclass


@dataclass
class Item:
    """
    Represents an item with its details.
    """
    id: str
    brand: str
    name: str

@dataclass
class ItemStock:
    """
    Represents the stock status of an item and its details.
    """
    item: Item
    url: str
    stock_status: str
    as_of: str
