import asyncio
import logging
from aiohttp import ClientSession
from discord.ext.commands import Bot
from discord.utils import get as discord_get
from matcha_notifier.enums import Website
from matcha_notifier.stock_task import StockTask
from matcha_notifier.restock_notifier import RestockNotifier
from matcha_notifier.stock_data import StockData
from source_clients import *
from yaml import safe_load


def setup_logging() -> None:
    """
    Set up logging configuration.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('matcha_notifier.log', mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

setup_logging()
logger = logging.getLogger(__name__)

with open('config.yaml') as f:
    config = safe_load(f)

SOURCE_MAPPER = {
    Website.IPPODO: IppodoScraper,
    Website.MARUKYU_KOYAMAEN: MarukyuKoyamaenScraper,
    Website.NAKAMURA_TOKICHI: NakamuraTokichiScraper,
    Website.SAZEN: SazenScraper,
    Website.STEEPING_ROOM: SteepingRoomScraper,
}

POLLING_INTERVAL_EXCEPTIONS = {
    Website.IPPODO: 'IPPODO_POLL_INTERVAL',
    Website.SAZEN: 'SAZEN_POLL_INTERVAL',
}

async def run(bot: Bot) -> bool:
    async with ClientSession() as session:
        stock_data = StockData()
        all_items = {}

        # Create a polling task for each scraper
        for website, scraper_class in SOURCE_MAPPER.items():
            scraper = scraper_class(session)
            polling_interval = config.get(
                POLLING_INTERVAL_EXCEPTIONS.get(website),
                config.get('DEFAULT_POLL_INTERVAL', 60)
            )
            task = StockTask(
                website, scraper, polling_interval, all_items,
                stock_data
            )
            asyncio.create_task(task.run())

        restock_channel = discord_get(bot.get_all_channels(), name='restock-alerts')
        if restock_channel:
            logger.info('restock-alerts channel connected')

            notifier = RestockNotifier(bot, restock_channel)
            asyncio.create_task(
                notifier.send_alerts(all_items, stock_data)
            )
        else:
            logger.warning(
                'Failed to notify on restocks - restock-alerts channel not found'
            )

        await asyncio.Event().wait()  # Keep the session alive

if __name__ == '__main__':
   asyncio.run(run())
