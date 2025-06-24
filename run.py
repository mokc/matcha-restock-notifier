import logging
from matcha_notifier.scraper import Scraper
from matcha_notifier.stock_data import StockData


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

    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
setup_logging()

def run() -> bool:
    scraper = Scraper()
    all_items = scraper.scrape_all()

    # Determine if there is a stock change
    instock_items = StockData().update_stock_changes(all_items)
    
    # TODO Notify users on the products that changed from out of stock to instocks

    print('NEW INSTOCK ITEMS')
    print(instock_items)
    return True
    

if __name__ == '__main__':
   run()