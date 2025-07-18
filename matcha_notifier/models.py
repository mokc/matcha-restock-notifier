from dataclasses import dataclass
from matcha_notifier.enums import Brand, StockStatus
from typing import Dict


@dataclass
class Item:
    """
    Represents an item with its details.
    """
    id: str
    brand: Brand
    name: str
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "brand": self.brand.value,  # convert enum to value
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        return cls(
            id=data["id"],
            brand=Brand(data["brand"]),
            name=data["name"]
        )

@dataclass
class ItemStock:
    """
    Represents the stock status of an item and its details.
    """
    item: Item
    url: str
    stock_status: StockStatus
    as_of: str
    
    def to_dict(self) -> Dict:
        return {
            "item": self.item.to_dict(),
            "url": self.url,
            "stock_status": self.stock_status.value,  # convert enum to value
            "as_of": self.as_of
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ItemStock':
        return cls(
            item=Item.from_dict(data["item"]),
            url=data["url"],
            stock_status=StockStatus(data["stock_status"]),
            as_of=data["as_of"]
        )