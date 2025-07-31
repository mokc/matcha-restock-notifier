import pytest
from aiohttp import ClientError
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.models import Item, ItemStock
from source_clients.marukyu_koyamaen_scraper import MarukyuKoyamaenScraper

class MockResponse:
    def __init__(self, text):
        self.text = text
        self.is_redirect = False
        self.raise_for_status = lambda: None
        self.status_code = 200

@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()

@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_mk_scraper_success(monkeypatch, mock_session, mock_response, mk_request):
    mock_response.content = mk_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.scraper.ClientSession', mock_session)

    scraper = MarukyuKoyamaenScraper(mock_session)
    resp = await scraper.scrape()
    
    assert len(resp) == 51
    assert resp['1186000CC-1C83000CC'] == ItemStock(
        item=Item(
            id='1186000CC-1C83000CC',
            brand=Brand.MARUKYU_KOYAMAEN,
            name='Sweetened Matcha – Excellent'
        ),
        as_of='2025-06-12 03:00:00,000',
        url='https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
        stock_status=StockStatus.INSTOCK
    )
    assert resp['1G28200C6'] == ItemStock(
        item=Item(
            id='1G28200C6',
            brand=Brand.MARUKYU_KOYAMAEN,
            name='Hojicha Mix',
        ),
        as_of='2025-06-12 03:00:00,000',
        url='https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
        stock_status=StockStatus.INSTOCK
    )
    assert resp['1G9D000CC-1GAD200C6'] == ItemStock(
        item=Item(
            id='1G9D000CC-1GAD200C6',
            brand=Brand.MARUKYU_KOYAMAEN,
            name='Matcha Mix'
        ),
        as_of='2025-06-12 03:00:00,000',
        url='https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
        stock_status=StockStatus.INSTOCK
    )
    instock_ids = {'1186000CC-1C83000CC', '1G28200C6', '1G9D000CC-1GAD200C6'}
    for item_id, data in resp.items():
        if item_id not in instock_ids:
            assert data.stock_status == StockStatus.OUT_OF_STOCK


@pytest.mark.asyncio
async def test_mk_scraper_no_instock_products(monkeypatch, mock_response, mock_session):
    mock_response.content = '<html><body>No products</body></html>'
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.scraper.ClientSession', mock_response)

    scraper = MarukyuKoyamaenScraper(mock_session)
    resp = await scraper.scrape()
    
    assert resp == {}

@pytest.mark.asyncio
async def test_mk_scraper_request_fail(monkeypatch, mock_response, mock_session):
    def mock_raise_for_status():
        raise ClientError("Failed to fetch URL")
    
    mock_response.raise_for_status = mock_raise_for_status
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.scraper.ClientSession', mock_session)

    scraper = MarukyuKoyamaenScraper(mock_session)
    resp = await scraper.scrape()
    
    assert resp == {}
