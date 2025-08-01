import pytest
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus, Website
from matcha_notifier.stock_data import StockData
from source_clients.steeping_room_scraper import SteepingRoomScraper
from unittest.mock import AsyncMock


@pytest.fixture
def sr_request():
    with open('tests/fixtures/steeping_room_fixture.html') as f:
        return f.read()
    
@pytest.mark.asyncio
async def test_sr_scraper_success(monkeypatch, mock_session, mock_response, sr_request):
    mock_response.content = sr_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.scraper.ClientSession', mock_session)
    
    scraper = SteepingRoomScraper(mock_session)
    all_items = await scraper.scrape()
    
    assert len(all_items) == 37 # Item count is 50 if including non-matcha items
    sd = StockData()
    instock_items, _ = sd.get_stock_changes({Website.STEEPING_ROOM: all_items}, {})
    
    assert len(instock_items) == 1
    assert len(instock_items[Website.STEEPING_ROOM]) == 5
    
    item_9092534599903 = instock_items[Website.STEEPING_ROOM]['9092534599903']
    assert item_9092534599903.item.name == 'Yame Matcha Blend'
    assert item_9092534599903.item.brand == Brand.UNKNOWN
    assert item_9092534599903.stock_status == StockStatus.INSTOCK
    
    item_8386781446367 = all_items['8386781446367']
    assert item_8386781446367.item.name == 'Aoarashi Matcha'
    assert item_8386781446367.item.brand == Brand.MARUKYU_KOYAMAEN
    assert item_8386781446367.stock_status == StockStatus.OUT_OF_STOCK

@pytest.mark.asyncio
async def test_sr_scraper_no_get_response():
    scraper = SteepingRoomScraper(AsyncMock())
    
    resp = await scraper.scrape()

    assert resp == {}

@pytest.mark.asyncio
async def test_sr_scraper_fuzzy_brand_matching(monkeypatch, mock_session, mock_response, sr_request):
    mock_response.content = sr_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.scraper.ClientSession', mock_session)
    
    scraper = SteepingRoomScraper(mock_session)
    all_items = await scraper.scrape()
    
    assert len(all_items) == 37 # Item count is 50 if including non-matcha items
    
    # slug is 'ogurayama-matcha-by-yamamasa-koyamaen-40-gram-tin-or-100-gram-bag'
    # Ensure that Yamamasa Koyamaen is assigned as the brand
    matcha = all_items['8820106690783']
    assert matcha.item.name == 'Ogurayama Matcha'
    assert matcha.item.brand == Brand.YAMAMASA_KOYAMAEN
