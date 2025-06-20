import logging
import pytest
import requests
from bs4 import BeautifulSoup
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

def test_mk_scraper_success(monkeypatch, mk_request):
    def mock_get(url):
        return MockResponse(mk_request)
    
    def mock_beautiful_soup(text, parser):
        return BeautifulSoup(mk_request, 'html.parser')
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.BeautifulSoup', mock_beautiful_soup)
    scraper = MarukyuKoyamaenScraper()
    resp = scraper.build()
    
    assert resp == {
        '1186000CC-1C83000CC': {
            'name': 'Sweetened Matcha – Excellent',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc'
        },
        '1G28200C6': {
            'name': 'Hojicha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6'
        },
        '1G9D000CC-1GAD200C6': {
            'name': 'Matcha Mix', 
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc'
        }
    }

def test_mk_scraper_no_instock_products(monkeypatch):
    def mock_get(url):
        return MockResponse('<html><body>No products</body></html>')
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    
    scraper = MarukyuKoyamaenScraper()
    resp = scraper.build()
    
    assert resp == {}

def test_mk_scraper_request_fail(monkeypatch):
    def mock_get(url):
        raise requests.RequestException("Failed to fetch URL")
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    
    scraper = MarukyuKoyamaenScraper()
    resp = scraper.build()
    
    assert resp == {}

