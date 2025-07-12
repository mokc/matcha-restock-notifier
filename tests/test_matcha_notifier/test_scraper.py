import logging
import pytest
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.scraper import Scraper


logger = logging.getLogger(__name__)

@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()

@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_scraper_scrapes_one_site(mock_session, mock_response, mk_request):
    mock_response.content = mk_request
    session = mock_session()
    session.get = lambda *args, **kwargs: mock_response

    scraper = Scraper(session)
    all_items = await scraper.scrape_one(Brand.MARUKYU_KOYAMAEN)
    assert isinstance(all_items, dict)
    assert len(all_items) == 51
    instock_items = {item : data for item, data in all_items.items() if data['stock_status'] == 'instock'}
    assert len(instock_items) == 3
    assert instock_items == {
        '1186000CC-1C83000CC': {
            'datetime': '2025-06-12 03:00:00,000',
            'brand': 'Marukyu Koyamaen',
            'name': 'Sweetened Matcha – Excellent',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
            'stock_status': StockStatus.INSTOCK.value
        },
        '1G28200C6': {
            'datetime': '2025-06-12 03:00:00,000',
            'brand': 'Marukyu Koyamaen',
            'name': 'Hojicha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
            'stock_status': StockStatus.INSTOCK.value
        },
        '1G9D000CC-1GAD200C6': {
            'datetime': '2025-06-12 03:00:00,000',
            'brand': 'Marukyu Koyamaen',
            'name': 'Matcha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
            'stock_status': StockStatus.INSTOCK.value
            }
        }

@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_scraper_scrapes_all_sites(mock_session, mock_response, mk_request):
    mock_response.content = mk_request
    session = mock_session()
    session.get = lambda *args, **kwargs: mock_response

    scraper = Scraper(session)
    all_items = await scraper.scrape_all()
    assert isinstance(all_items, dict)
    assert len(all_items[Brand.MARUKYU_KOYAMAEN]) == 51
    instock_items = {item : data for item, data in all_items[Brand.MARUKYU_KOYAMAEN].items() if data['stock_status'] == 'instock'}
    assert len(instock_items) == 3
    assert instock_items == {
        '1186000CC-1C83000CC': {
            'datetime': '2025-06-12 03:00:00,000',
            'brand': 'Marukyu Koyamaen',
            'name': 'Sweetened Matcha – Excellent',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
            'stock_status': 'instock'
        },
        '1G28200C6': {
            'datetime': '2025-06-12 03:00:00,000',
            'brand': 'Marukyu Koyamaen',
            'name': 'Hojicha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
            'stock_status': 'instock'
        },
        '1G9D000CC-1GAD200C6': {
            'datetime': '2025-06-12 03:00:00,000',
            'brand': 'Marukyu Koyamaen',
            'name': 'Matcha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
            'stock_status': 'instock'
        }
    }

@pytest.mark.asyncio
async def test_scraper_no_instock_items(monkeypatch, mock_session, mock_response):   
    mock_response.content = '<html></html>'
    session = mock_session()
    session.get = lambda *args, **kwargs: mock_response

    scraper = Scraper(session)
    instock_items = await scraper.scrape_all()
    assert instock_items == {}  # Expecting no items to be returned
