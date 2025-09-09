import logging
from aiohttp import ClientSession
from matcha_notifier.base_scraper import BaseScraper
from source_clients import *
from typing import Dict


logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, session: ClientSession, scraper: BaseScraper):
        self.session = session
        self.scraper = scraper

    async def scrape(self) -> Dict:
        all_items = await self.scraper(self.session).scrape()
        if all_items:
            return all_items

        return {}