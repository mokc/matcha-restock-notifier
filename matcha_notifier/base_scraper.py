import aiofiles
import logging
from abc import ABC, abstractmethod
from aiohttp import ClientError, ClientSession, ClientTimeout
from asyncio import CancelledError
from datetime import datetime
from matcha_notifier.enums import Brand
from matcha_notifier.models import ItemStock
from pathlib import Path
from typing import Dict, Set
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self):
        if not hasattr(self, 'catalog_url'):
            raise AttributeError(
                'Subclasses must define \'self.catalog_url\' in __init__.'
            )
        self.unknown_brands_file = 'unknown_brands.txt'
    
    @abstractmethod
    async def scrape(self) -> Dict[str, ItemStock]:
        """
        Scrape the website and return a dictionary of item IDs to ItemStock objects.
        """
        pass
    
    async def fetch_url(
        self,
        url: str,
        session: ClientSession,
        timeout: ClientTimeout = ClientTimeout(total=10)
    ) -> str:
        """
        Fetch the content of a URL with the specified timeout.
        """
        timeout = ClientTimeout(total=10)
        try:
            async with session.get(url, timeout=timeout) as resp:
                if len(resp.history) > 0:   # Log warning if redirected
                    logger.warning(
                        f'Redirected from {url} to {resp.url}'
                    )

                resp.raise_for_status()  # Raise an error for bad responses
                logger.info(
                    f'Fetched URL: {url} with status {resp.status}'
                )
                text = await resp.text()
        except CancelledError:
            logger.error(f'Request to {url} timed out')
            return ''
        except ClientError as e:
            logger.error(f'Error fetching {url}: {e}')
            return ''
        except Exception as e:
            logger.error(f'Unexpected error fetching {url}: {e}')
            return ''
        
        return text
    
    def get_as_of(self) -> str:
        """
        Get the current timestamp in a specific format
        """
        now = datetime.now(ZoneInfo('America/Los_Angeles'))
        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S,') + f'{int(now.microsecond / 1000):03d}'
        return formatted_time

    def is_matcha_powder(self, name: str) -> bool:
        """
        Return True if the item is a matcha powder. This is determined by
        checking against a set of keywords that are other matcha-related items
        """
        excluded_keywords = {
            'sifter', 'hojicha', 'houjicha', 'bowl', 'scoop', 'whisk'
        }
        lower_name = name.lower()
        return not any(keyword in lower_name for keyword in excluded_keywords)
        
    async def load_unknown_brands(self) -> Set[str]:
        """
        Load unknown brands from the unknown_brands.txt file.
        """
        if not Path(self.unknown_brands_file).exists():
            return set()

        async with aiofiles.open(self.unknown_brands_file, mode='r') as f:
            content = await f.read()
            return set(line.strip() for line in content.splitlines() if line.strip())

    async def log_unknown_brand(self, brand: str) -> None:
        """
        Log an unknown matcha brand to the unknown_brands.txt file.
        """
        existing = await self.load_unknown_brands()
        if brand not in existing:
            async with aiofiles.open(self.unknown_brands_file, 'a') as f:
                await f.write(f'{brand}\n')

            logger.warning(f'Unknown brand logged: {brand}')

    def get_all_brands(self) -> Set[str]:
        """
        Get all known brands from the unknown_brands.txt file.
        """
        return set(b.value for b in Brand)

    async def match_to_brand(self, brand: str) -> Brand:
        """
        Match the brand name to a known Brand enum. If no match is found,
        return Brand.UNKNOWN and log the brand to unknown_brands.txt.
        """
        lower_brand = brand.lower()
        all_brands = self.get_all_brands()
        # Prioritize longer brand names to avoid partial matches
        for brand_enum in sorted(all_brands, key=len, reverse=True):
            if brand_enum.lower() in lower_brand:
                return Brand(brand_enum)
        
        # If no match found, log the unknown brand
        await self.log_unknown_brand(brand)
        return Brand.UNKNOWN
