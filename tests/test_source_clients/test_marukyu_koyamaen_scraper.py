import logging
import pytest
import requests
from bs4 import BeautifulSoup
from freezegun import freeze_time
from source_clients.marukyu_koyamaen_scraper import MarukyuKoyamaenScraper


logger = logging.getLogger(__name__)

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
async def test_mk_scraper_success(monkeypatch, mk_request):
    def mock_get(url):
        return MockResponse(mk_request)
    
    def mock_beautiful_soup(text, parser):
        return BeautifulSoup(mk_request, 'html.parser')
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.BeautifulSoup', mock_beautiful_soup)
    scraper = MarukyuKoyamaenScraper()
    resp = await scraper.scrape()
    
    assert len(resp) == 51
    assert resp['1186000CC-1C83000CC'] == {
        'datetime': '2025-06-12T03:00:00-07:00',
        'name': 'Sweetened Matcha – Excellent',
        'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
        'stock_status': 'instock'
    }
    assert resp['1G28200C6'] == {
        'datetime': '2025-06-12T03:00:00-07:00',
        'name': 'Hojicha Mix',
        'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
        'stock_status': 'instock'
    }
    assert resp['1G9D000CC-1GAD200C6'] ==  {
        'datetime': '2025-06-12T03:00:00-07:00',
        'name': 'Matcha Mix', 
        'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
        'stock_status': 'instock'
    }
    instock_ids = {'1186000CC-1C83000CC', '1G28200C6', '1G9D000CC-1GAD200C6'}
    for item_id, data in resp.items():
        if item_id not in instock_ids:
            assert data['stock_status'] == 'outofstock'


@pytest.mark.asyncio
async def test_mk_scraper_no_instock_products(monkeypatch):
    def mock_get(url):
        return MockResponse('<html><body>No products</body></html>')
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    
    scraper = MarukyuKoyamaenScraper()
    resp = await scraper.scrape()
    
    assert resp == {}

@pytest.mark.asyncio
async def test_mk_scraper_request_fail(monkeypatch):
    def mock_get(url):
        raise requests.RequestException("Failed to fetch URL")
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    
    scraper = MarukyuKoyamaenScraper()
    resp = await scraper.scrape()
    
    assert resp == {}

