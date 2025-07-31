import ast
import logging
import re
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from matcha_notifier.base_scraper import BaseScraper
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.models import Item, ItemStock
from typing import Dict


logger = logging.getLogger(__name__)

class MarukyuKoyamaenScraper(BaseScraper):
    def __init__(self, session: ClientSession):
        self.session = session
        self.catalog_url = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/catalog/matcha'
        self.product_url = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/'
        super().__init__()      # Must be called after setting catalog_url

    async def scrape(self) -> Dict[str, ItemStock]:

        text = await self.fetch_url(self.catalog_url, self.session)
        if not text:
            return {}
    
        all_items = self.parse_products(text)
        return all_items

    def parse_products(self, text: str) -> Dict[str, ItemStock]:
        """
        Parse product data from the HTML soup and return a dictionary of ItemStock.
        """
        soup = BeautifulSoup(text, 'html.parser')
        products = soup.find_all(class_=re.compile('product product-type-variable'))
        all_items = {}      # Stores data on all matcha products
        for product in products:
            item_data = ast.literal_eval(product.a['data-item'])
            item_id = item_data['item_id']
            url = product.a['href']
            if 'outofstock' in product['class']:
                stock_status = StockStatus.OUT_OF_STOCK
            else:
                stock_status = StockStatus.INSTOCK

            item = Item(
                id=item_id,
                brand=Brand.MARUKYU_KOYAMAEN,
                name=item_data['item_name']
            )

            all_items[item_id] = ItemStock(
                item=item,
                url=url,
                as_of=self.get_as_of(),
                stock_status=stock_status
            )
        
        return all_items
