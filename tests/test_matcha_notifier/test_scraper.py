import pytest
from bs4 import BeautifulSoup
from freezegun import freeze_time
from matcha_notifier.enums import Brand
from matcha_notifier.scraper import Scraper


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

@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
def test_scraper_scrapes_one(monkeypatch, mk_request):
    def mock_get(url):
        return MockResponse(mk_request)
    
    def mock_beautiful_soup(text, parser):
        return BeautifulSoup(mk_request, 'html.parser')
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.BeautifulSoup', mock_beautiful_soup)
    
    scraper = Scraper()
    instock_items = scraper.scrape_one(Brand.MARUKYU_KOYAMAEN)
    assert isinstance(instock_items, dict)
    assert len(instock_items) == 3
    assert instock_items == {
        '1186000CC-1C83000CC': {
            'datetime': '2025-06-12T03:00:00-07:00',
            'name': 'Sweetened Matcha – Excellent',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
            'stock_status': 'instock'
        },
        '1G28200C6': {
            'datetime': '2025-06-12T03:00:00-07:00',
            'name': 'Hojicha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
            'stock_status': 'instock'
        },
        '1G9D000CC-1GAD200C6': {
            'datetime': '2025-06-12T03:00:00-07:00',
            'name': 'Matcha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
            'stock_status': 'instock'
            }
        }

@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
def test_scraper_scrapes_all(monkeypatch, mk_request):
    def mock_get(url):
        return MockResponse(mk_request)
    
    def mock_beautiful_soup(text, parser):
        return BeautifulSoup(mk_request, 'html.parser')
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.BeautifulSoup', mock_beautiful_soup)
    
    scraper = Scraper()
    instock_items = scraper.scrape_all()
    assert isinstance(instock_items, dict)
    assert len(instock_items[Brand.MARUKYU_KOYAMAEN]) == 3
    assert instock_items == {
        Brand.MARUKYU_KOYAMAEN: {
            '1186000CC-1C83000CC': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Sweetened Matcha – Excellent',
                'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
                'stock_status': 'instock'
            },
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Hojicha Mix',
                'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
                'stock_status': 'instock'
            },
            '1G9D000CC-1GAD200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'name': 'Matcha Mix',
                'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
                'stock_status': 'instock'
            }
        }
    }


def test_scraper_no_instock_items(monkeypatch):
    def mock_get(url):
        return MockResponse('<html></html>')  # Empty HTML for no products

    def mock_beautiful_soup(text, parser):
        return BeautifulSoup('<html></html>', 'html.parser')
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.BeautifulSoup', mock_beautiful_soup)
    
    scraper = Scraper()
    instock_items = scraper.scrape_all()
    assert instock_items == {}  # Expecting no items to be returned
