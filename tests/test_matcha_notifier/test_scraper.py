import logging
import pytest
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus, Website
from matcha_notifier.models import Item, ItemStock
from matcha_notifier.scraper import Scraper
from source_clients.marukyu_koyamaen_scraper import MarukyuKoyamaenScraper


logger = logging.getLogger(__name__)

@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()

@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_scraper_success(mock_session, mock_response, mk_request):
    mock_response.content = mk_request
    session = mock_session()
    session.get = lambda *args, **kwargs: mock_response

    scraper = Scraper(session, MarukyuKoyamaenScraper)
    all_items = await scraper.scrape()
    assert isinstance(all_items, dict)
    assert len(all_items) == 51
    instock_items = {
        item:data for item, data in all_items.items() if data.stock_status == StockStatus.INSTOCK
    }
    assert len(instock_items) == 3
    assert instock_items == {
        '1186000CC-1C83000CC': ItemStock(
            item=Item(
                id='1186000CC-1C83000CC',
                brand=Brand.MARUKYU_KOYAMAEN,
                name='Sweetened Matcha – Excellent' 
            ),
            as_of='2025-06-12 03:00:00,000',
            url='https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
            stock_status=StockStatus.INSTOCK
        ),
        '1G28200C6': ItemStock(
            item=Item(
                id='1G28200C6',
                brand=Brand.MARUKYU_KOYAMAEN,
                name='Hojicha Mix'
            ),
            as_of='2025-06-12 03:00:00,000',
            url='https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
            stock_status=StockStatus.INSTOCK
        ),
        '1G9D000CC-1GAD200C6': ItemStock(
            item=Item(
                id='1G9D000CC-1GAD200C6',
                brand=Brand.MARUKYU_KOYAMAEN,
                name='Matcha Mix'
            ),
            as_of='2025-06-12 03:00:00,000',
            url='https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
            stock_status=StockStatus.INSTOCK
        )
    }

@pytest.mark.asyncio
async def test_scraper_no_items(monkeypatch, mock_session, mock_response):   
    mock_response.content = '<html></html>'
    session = mock_session()
    session.get = lambda *args, **kwargs: mock_response

    scraper = Scraper(session, MarukyuKoyamaenScraper)
    instock_items = await scraper.scrape()
    assert instock_items == {}  # Expecting no items to be returned
