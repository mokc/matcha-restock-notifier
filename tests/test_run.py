
import json
import pytest
from bs4 import BeautifulSoup
from matcha_notifier.run import run

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
async def test_run(monkeypatch, mk_request):
    def mock_get(url):
        return MockResponse(mk_request)

    def mock_beautiful_soup(text, parser):
        return BeautifulSoup(mk_request, 'html.parser')
    
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.requests.get', mock_get)
    monkeypatch.setattr('source_clients.marukyu_koyamaen_scraper.BeautifulSoup', mock_beautiful_soup)
    result = await run()
    
    assert result is True
