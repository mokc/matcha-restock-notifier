import pytest
from matcha_notifier.stock_data import StockData
from matcha_notifier.enums import StockStatus, Website
from source_clients.ippodo_scraper import IppodoScraper
from unittest.mock import AsyncMock, Mock


@pytest.fixture
def ippodo_request():
    with open('tests/fixtures/ippodo_fixture.html') as file:
        return file.read()

@pytest.mark.asyncio
async def test_ippodo_scraper(monkeypatch, mock_session, mock_response, ippodo_request):
    mock_response.content = ippodo_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('source_clients.ippodo_scraper.ClientSession', mock_session)

    scraper = IppodoScraper(mock_session)
    result = await scraper.scrape()

    assert result is not None
    assert isinstance(result, dict)
    assert len(result) == 24
    
    instock_items, _ = StockData().get_stock_changes({Website.IPPODO: result}, {})
    assert len(instock_items) == 1
    items = instock_items[Website.IPPODO]
    assert len(items) == 3
    assert items['4982833125517'].stock_status == StockStatus.INSTOCK
    assert items['4982833642298'].stock_status == StockStatus.INSTOCK
    assert items['4982833642120'].stock_status == StockStatus.INSTOCK

@pytest.mark.asyncio
async def test_ippodo_scraper_collection_json_missing(
    monkeypatch, mock_response, mock_session
):
    """
    Test the case where the collection JSON is missing from the page.
    """
    mock_response.content = ippodo_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('source_clients.ippodo_scraper.ClientSession', mock_session)
    soup = Mock()
    soup.find_all.return_value = [] 
    monkeypatch.setattr(
        'source_clients.ippodo_scraper.BeautifulSoup', lambda *args, **kwargs:soup
    )

    scraper = IppodoScraper(mock_session)
    result = await scraper.scrape()

    assert result == {}
