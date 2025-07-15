
import ast
import logging
import re
from aiohttp import ClientError, ClientSession, ClientTimeout
from asyncio import TimeoutError
from bs4 import BeautifulSoup
from datetime import datetime
from matcha_notifier.base_scraper import BaseScraper
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.models import Item, ItemStock
from typing import Dict
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

class MarukyuKoyamaenScraper(BaseScraper):
    def __init__(self, session: ClientSession):
        self.session = session
        self.catalog_url = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/catalog/matcha'
        self.product_url = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/'

    async def scrape(self) -> Dict[str, ItemStock]:
        # Fetch URL
        timeout = ClientTimeout(total=10)
        try:
            async with self.session.get(self.catalog_url, timeout=timeout) as resp:
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
        except TimeoutError:
            logger.error(f'Request to {self.catalog_url} timed out')
            return {}
        except ClientError as e:
            logger.error(f'Error fetching {self.catalog_url}: {e}')
            return {}

        soup = BeautifulSoup(text, 'html.parser')
        products = soup.find_all(class_=re.compile('product product-type-variable'))

        all_items = {}      # Stores data on all matcha products
        for product in products:
            item_data = ast.literal_eval(product.a['data-item'])
            item_id = item_data['item_id']
            now = datetime.now(ZoneInfo('America/Los_Angeles'))
            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S,') + f'{int(now.microsecond / 1000):03d}'
            url = product.a['href']
            if 'outofstock' in product['class']:
                stock_status = StockStatus.OUT_OF_STOCK.value
            else:
                stock_status = StockStatus.INSTOCK.value

            item = Item(
                id=item_id,
                brand=Brand.MARUKYU_KOYAMAEN.value,
                name=item_data['item_name']
            )

            all_items[item_id] = ItemStock(
                item=item,
                url=url,
                as_of=formatted_time,
                stock_status=stock_status
            )
        
        return all_items
