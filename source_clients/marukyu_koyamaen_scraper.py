
import ast
import logging
import re
from aiohttp import ClientSession, ClientError
from bs4 import BeautifulSoup
from datetime import datetime
from matcha_notifier.enums import Brand, StockStatus
from typing import Dict
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

class MarukyuKoyamaenScraper:
    def __init__(self, session: ClientSession):
        self.session = session
        self.catalog_url = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/catalog/matcha'
        self.product_url = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/'

    async def scrape(self) -> Dict:
        # Fetch URL
        try:
            async with self.session.get(self.catalog_url) as resp:
                if len(resp.history) > 0:   # Log warning if redirected
                    logger.warning(
                        f'Redirected from {self.catalog_url} to {resp.url}'
                    )

                resp.raise_for_status()  # Raise an error for bad responses
                logger.info(
                    f'Fetched catalog URL: {self.catalog_url} with status '
                    f'{resp.status}'
                )
                text = await resp.text()
        except ClientError as e:
            logger.error(f'Error fetching {self.catalog_url}: {e}')
            return {}

        soup = BeautifulSoup(text, 'html.parser')
        products = soup.find_all(class_=re.compile('product product-type-variable'))

        all_items = {}      # Stores data on all matcha products
        for product in products:
            item_data = ast.literal_eval(product.a['data-item'])
            item_id = item_data['item_id']
            all_items[item_id] = {
                'datetime': datetime.now(ZoneInfo('America/Los_Angeles')).isoformat(),
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': item_data['item_name'],
                'url': product.a['href'],
            }

            if 'outofstock' in product['class']:
                all_items[item_id]['stock_status'] = StockStatus.OUT_OF_STOCK.value
            else:
                all_items[item_id]['stock_status'] = StockStatus.INSTOCK.value
        
        return all_items
