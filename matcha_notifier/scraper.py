from matcha_notifier.enums import Brand
from source_clients.marukyu_koyamaen_scraper import MarukyuKoyamaenScraper
from typing import Dict


SOURCE_MAPPER = {
        Brand.MARUKYU_KOYAMAEN: MarukyuKoyamaenScraper
    }

class Scraper:
    def __init__(self):
        pass

    def scrape_one(self, source: Brand) -> Dict:
        company_scraper = SOURCE_MAPPER[source]
        instock_items = company_scraper().build()
        if instock_items:
            return instock_items
    
    def scrape_all(self) -> Dict:
        all_instock_items = {}
        for source in SOURCE_MAPPER:
            instock_items = self.scrape_one(source)
            if instock_items:
                all_instock_items[source] = instock_items

        return all_instock_items

    