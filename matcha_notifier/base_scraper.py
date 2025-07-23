from abc import ABC, abstractmethod
from aiohttp import ClientTimeout
from matcha_notifier.models import ItemStock
from typing import Dict


class BaseScraper(ABC):
    def __init__(self):
        self.timeout = ClientTimeout(total=10)

    @abstractmethod
    async def scrape(self) -> Dict[str, ItemStock]:
        """
        Scrape the website and return a dictionary of item IDs to ItemStock objects.
        """
        pass