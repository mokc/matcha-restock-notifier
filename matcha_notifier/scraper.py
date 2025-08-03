from aiohttp import ClientSession
from matcha_notifier.enums import Website
from source_clients import *
from typing import Dict


SOURCE_MAPPER = {
        Website.MARUKYU_KOYAMAEN: MarukyuKoyamaenScraper,
        Website.STEEPING_ROOM: SteepingRoomScraper,
        Website.NAKAMURA_TOKICHI: NakamuraTokichiScraper
    }

class Scraper:
    def __init__(self, session: ClientSession):
        self.session = session

    async def scrape_one(self, source: Website) -> Dict:
        company_scraper = SOURCE_MAPPER[source]
        all_items = await company_scraper(self.session).scrape()
        if all_items:
            return all_items
    
    async def scrape_all(self) -> Dict:
        all_instock_items = {}

        for source in SOURCE_MAPPER:
            all_items = await self.scrape_one(source)
            if all_items:
                all_instock_items[source] = all_items

        return all_instock_items

    