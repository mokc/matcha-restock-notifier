import logging
from aiohttp import ClientSession
from bs4 import BeautifulSoup, element
from matcha_notifier.base_scraper import BaseScraper
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.models import Item, ItemStock
from typing import Dict


logger = logging.getLogger(__name__)

class SazenScraper(BaseScraper):
    def __init__(self, session: ClientSession):
        self.session = session
        self.catalog_url = 'https://www.sazentea.com/en/products/c22-ceremonial-grade-matcha'
        self.product_url = 'https://www.sazentea.com'
        super().__init__()

    async def scrape(self) -> Dict[str, ItemStock]:
        text = await self.fetch_url(self.catalog_url, self.session)
        if not text:
            return {}

        all_items = await self.parse_products(text)
        return all_items

    async def parse_products(self, text: str) -> Dict[str, ItemStock]:
        soup = BeautifulSoup(text, 'html.parser')
        products = soup.find_all(class_='product')
        all_items = {}

        for product in products:
            # Ignore the bestsellers section
            if 'bestseller' in product['class']:
                continue

            name = product['data-name']
            url = self.product_url + product.a['href']
            stock_status = StockStatus.INSTOCK

            product_page = await self.fetch_url(url, self.session)
            product_soup = BeautifulSoup(product_page, 'html.parser')
            product_info = product_soup.select_one('div#product-info')
            item_id = self._parse_item_id(product_info)
            brand = self._parse_brand(product_info)

            item = Item(
                id=item_id,
                brand=brand,
                name=name,
            )
            all_items[item_id] = ItemStock(
                item=item,
                url=url,
                as_of=self.get_as_of(),
                stock_status=stock_status
            )

        return all_items
    
    def _parse_item_id(self, product_info: element.Tag) -> str:
        item_code_tag = product_info.find('span', string='Item code:')
        item_id = item_code_tag.next_sibling.strip()
        return item_id
    
    def _parse_brand(self, product_info: element.Tag) -> Brand:
        brand_tag = product_info.find('span', string='Maker:')
        brand = self.match_to_brand(brand_tag.next_sibling.strip())
        return brand