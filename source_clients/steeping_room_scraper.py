import logging
import os
import traceback
from aiohttp import ClientSession
from bs4 import BeautifulSoup, element
from matcha_notifier.base_scraper import BaseScraper
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.models import Item, ItemStock
from typing import Dict, List, Tuple


logger = logging.getLogger(__name__)

class SteepingRoomScraper(BaseScraper):
    def __init__(self, session: ClientSession):
        self.session = session
        self.catalog_url = 'https://www.thesteepingroom.com/collections/matcha-tea'
        self.product_url = 'https://www.thesteepingroom.com/'
        super().__init__()      # Must be called after setting catalog_url
        
    async def scrape(self) -> Dict[str, ItemStock]:
        text = await self.fetch_url(self.catalog_url, self.session)
        if not text:
            return {}

        all_items = await self.parse_products(text)
        return all_items
    
    async def parse_products(self, text: str) -> Dict[str, ItemStock]:
        soup = BeautifulSoup(text, 'html.parser')
        products = soup.find_all(
            lambda tag: (
                any(cls.startswith('product-') for cls in tag.get('class', []))
                and tag.find('div', class_='product-wrap', recursive=False) is not None
            )
        )
        all_items = {}
        for product in products:
            item_id = self._extract_item_id(product)
            item_data = product.find('div', class_='relative product_image')
            # href in format of '/products/{item}'
            url = self.product_url + item_data.a['href']
            name, brand = await self.name_brand_parser(url)
            # name and brand are empty strings if it isn't matcha powder
            if name == '' and brand == '':
                continue
            
            stock_data = product.next_sibling.next_sibling.find(class_='sold_out')
        
            if not stock_data:
                logger.warning(f'No stock data found for item {item_id}: {url}')
                continue
        
            if stock_data and stock_data.text.strip().lower() == 'sold out':
                stock_status = StockStatus.OUT_OF_STOCK
            else:
                stock_status = StockStatus.INSTOCK

            item = Item(
                id=item_id,
                brand=brand,
                name=name
            )
            
            all_items[item_id] = ItemStock(
                item=item,
                url=url,
                as_of=self.get_as_of(),
                stock_status=stock_status
            )
        
        return all_items
    
    def _extract_item_id(self, product: element.Tag) -> str:
        """
        Parses out item ID
        """
        # item id in format of 'product-9092534599903'
        item_id_offset = len('product-')
        return product['class'][0][item_id_offset:]

    async def name_brand_parser(self, url: str) -> Tuple[str, str]:
        """
        Parses out name and brand from the URL slug
        """
        url_split = url.split('/')
        sr_name = url_split[-1]
        sr_name_split = sr_name.split('-')
        has_by = False

        # Parse name, which is determined by everything before 'by'. If 'by'
        # isn't present, then the name is everything
        try:
            by_idx = sr_name_split.index('by')
            has_by = True
            name = ' '.join(sr_name_split[:by_idx]).title()
        except ValueError as e:
            name = ' '.join(sr_name_split).title()
            
        if not self.is_matcha_powder(name):
            return '', ''
            
        # Assign brand to a Brand enum if it exists, otherwise set to
        # Brand.UNKNOWN
        if has_by:
            str_brand = ' '.join(sr_name_split[by_idx+1:]).title()
            brand = self.match_to_brand(str_brand)
        else:
            brand = Brand.UNKNOWN

        return name, brand
