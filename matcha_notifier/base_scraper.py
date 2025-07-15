from abc import ABC, abstractmethod
from matcha_notifier.models import ItemStock
from typing import Dict


class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self) -> Dict[str, ItemStock]:
        """
        Scrape the website and return a dictionary of item IDs to ItemStock objects.
        """
        pass