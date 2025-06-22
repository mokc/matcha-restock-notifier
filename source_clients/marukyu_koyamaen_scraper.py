
import ast
import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

class MarukyuKoyamaenScraper:
    def __init__(self):
        self.catalog_url = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/catalog/matcha'
        self.product_url = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/'
        # TODO Pass in filters
    
    def build(self) -> Dict:
        # Fetch URL
        try:
            html = requests.get(self.catalog_url)
            
            if html.is_redirect:
                logger.warning(
                    f'Redirected from {self.catalog_url} to {html.url}'
                )

            html.raise_for_status()  # Raise an error for bad responses
            logger.info(
                f'Fetched catalog URL: {self.catalog_url} with status '
                f'{html.status_code}'
            )
        except requests.RequestException as e:
            logger.error(f'Error fetching {self.catalog_url}: {e}')
            return {}

        soup = BeautifulSoup(html.text, 'html.parser')
        products = soup.find_all(class_=re.compile('product product-type-variable'))

        all_instock_data = {}
        for product in products:
            # If a product is out of stock, we don't need to send a notification about it
            if 'outofstock' in product['class']:
                continue

            item_data = ast.literal_eval(product.a['data-item'])
            item_id = item_data['item_id']
            all_instock_data[item_id] = {
                'datetime': datetime.now(ZoneInfo('America/Los_Angeles')).isoformat(),
                'name': item_data['item_name'],
                'url': product.a['href']
            }
        
        return all_instock_data
