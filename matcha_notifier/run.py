import asyncio
import logging
from aiohttp import ClientSession
from discord.ext.commands import Bot
from matcha_notifier.restock_notifier import RestockNotifier
from matcha_notifier.scraper import Scraper
from matcha_notifier.stock_data import StockData
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
    
async def run(bot: Bot) -> bool:
    async with ClientSession() as session:
        scraper = Scraper(session)
        all_items = await scraper.scrape_all()

        # Determine if there is a stock change
        stock_data = StockData()
        state = await stock_data.load_state()
        new_instock_items, new_state = stock_data.get_stock_changes(
            all_items, state
        )
        
        if config['ENABLE_NOTIFICATIONS_FLAG'] is True:
            # Notify restocks-alert channel of all new/restocked items
            notifier = RestockNotifier(bot)
            is_notified = await notifier.notify_all_new_restocks(new_instock_items)

            # TODO For new/restocks, notify members who have subscribed to company/blend combination
        
        # If there are any changes, save the new state
        if new_state != state:
            # If there are no new instock items or if notifications were sent,
            # save the state
            if not new_instock_items or is_notified:
                await stock_data.save_state(new_state)
        
    if new_instock_items:
        logger.info('NEW INSTOCK ITEMS')
        logger.info(new_instock_items)
    return True

with open('config.yaml') as f:
    config = safe_load(f)

if __name__ == '__main__':
   asyncio.run(run())