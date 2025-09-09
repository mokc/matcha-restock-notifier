import asyncio
import logging
from matcha_notifier.enums import Website
from matcha_notifier.models import ItemStock
from matcha_notifier.scraper import Scraper
from matcha_notifier.stock_data import StockData
from typing import Dict


logger = logging.getLogger(__name__)

class StockTask:
    def __init__(
        self, website: Website, scraper: Scraper, interval: int,
        all_items: Dict[Website, Dict[str, ItemStock]], stock_data: StockData
    ):
        self.website = website
        self.scraper = scraper
        self.interval = interval
        self.all_items = all_items
        self.stock_data = stock_data

    async def run(self):
        while True:
            all_items = await self.poll()
            self.all_items[self.website] = all_items

            await asyncio.sleep(self.interval)

    async def poll(self) -> Dict[Website, Dict]:
        """
        Poll the website for stock data at a specified interval.
        """
        logger.info(f'Start polling {self.website.value} for stock data')
        try:
            all_items = await self.scraper.scrape()
            logger.info(f'Completed polling for {self.website.value}')

            return all_items
        except Exception as e:
            logger.error(f"Error while polling website: {e}")
            return {}