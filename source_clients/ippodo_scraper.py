import json
import logging
import quickjs
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.models import Item, ItemStock
from matcha_notifier.base_scraper import BaseScraper
from typing import Dict


logger = logging.getLogger(__name__)

class IppodoScraper(BaseScraper):
    def __init__(self, session: ClientSession):
        self.session = session
        self.catalog_url = 'https://ippodotea.com/collections/matcha'
        self.product_url = 'https://ippodotea.com'
        super().__init__()

    async def scrape(self):
        text = await self.fetch_url(self.catalog_url, self.session)
        if not text:
            return {}

        all_items = await self.parse_products(text)
        return all_items

    async def parse_products(self, text: str) -> Dict[str, ItemStock]:
        soup = BeautifulSoup(text, 'html.parser')
        script_tags = soup.find_all('script')
        script_tag = next((s for s in script_tags
                   if "collection_json" in s.get_text()), None)
        
        if not script_tag:
            logger.error('No collection JSON found in the page for Ippodo')
            return {}

        products = self._extract_collection_json(script_tag.text)
        all_items = {}

        for product in products:
            item_id = product['sku']
            name = product['title']
            if not self.is_matcha_powder(name):
                continue

            url = self.product_url + product['url']
            stock_status = (
                StockStatus.OUT_OF_STOCK if product['soldOut'] is True
                else StockStatus.INSTOCK
            )

            item = Item(
                id=item_id,
                brand=Brand.IPPODO,
                name=name,
            )
            all_items[item_id] = ItemStock(
                item=item,
                url=url,
                as_of=self.get_as_of(),
                stock_status=stock_status
            )

        return all_items
    
    def _extract_collection_json(self, js_text: str) -> dict:
        """
        Ippodo hardcodes the collection JSON in JavaScript in a script tag.
        Since Python does not have a built-in JavaScript interpreter,
        we use the quickjs library to evaluate the JavaScript and extract the
        JSON.
        """
        # Create a sandbox to run JavaScript
        ctx = quickjs.Context()
        ctx.eval(js_text)   # Execute the JavaScript code

        # Now read the variable value; quickjs converts to Python types
        result = ctx.eval("collection_json")
        if not isinstance(result, dict):
            # Sometimes the site wraps differently; as a fallback, try returning JSON string:
            result = ctx.eval("JSON.stringify(collection_json)")
            result = json.loads(result)
        return result['product']
