import logging
from aiohttp import ClientSession
from bs4 import BeautifulSoup, element
from matcha_notifier.base_scraper import BaseScraper
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.models import Item, ItemStock
from typing import Dict


logger = logging.getLogger(__name__)

class NakamuraTokichiScraper(BaseScraper):
    def __init__(self, session: ClientSession):
        self.session = session
        self.catalog_url = 'https://global.tokichi.jp/collections/matcha'
        self.product_url = 'https://global.tokichi.jp'
        super().__init__()  # Must be called after setting catalog_url

    async def scrape(self) -> Dict[str, ItemStock]:
        text = await self.fetch_url(self.catalog_url, self.session)
        if not text:
            return {}

        soup = BeautifulSoup(text, 'html.parser')
        all_items = self.parse_products(text, soup)

        # Handle pagination if necessary
        total_pages = self.get_total_pages(text, soup)
        for page in range(2, total_pages + 1):
            page_url = f"{self.catalog_url}?page={page}"
            text = await self.fetch_url(page_url, self.session)
            if not text:
                continue

            soup = BeautifulSoup(text, 'html.parser')
            all_items.update(self.parse_products(text, soup))
        return all_items

    def parse_products(self, text: str, soup: BeautifulSoup) -> Dict[str, ItemStock]:
        products = soup.select('.card-wrapper')
        all_items = {}
        
        for product in products:
            card_info = product.select('.card__information')
            card_image = card_info[0]
            item_id = self._extract_item_id(card_image)
            url = self.product_url + card_image.a['href']
            name = card_image.text.strip()
            if not name:
                continue

            oos = product.select('.price--sold-out')
            stock_status = StockStatus.OUT_OF_STOCK if oos else StockStatus.INSTOCK

            item = Item(
                id=item_id,
                brand=Brand.NAKAMURA_TOKICHI,
                name=name,
            )
            all_items[item_id] = ItemStock(
                item=item,
                url=url,
                stock_status=stock_status,
                as_of=self.get_as_of()
            )
        return all_items
    
    def _extract_item_id(self, card_image: element.Tag) -> str:
        """
        Extract the item ID from the card image element
        """
        # item_id in format 'StandardCardNoMediaLink-template--19535516958972__product-grid-9001332932860'
        item_id = card_image.a['id']
        return item_id.split('-')[-1]
        
    def get_total_pages(self, text: str, soup: BeautifulSoup) -> int:
        page_links = soup.select('.pagination__item[aria-label^="Page"]')
        if not page_links:
            return 1
        
        page_numbers = []
        for link in page_links:
            page_num = int(link.text.strip())
            page_numbers.append(page_num)

        return max(page_numbers) if page_numbers else 1
