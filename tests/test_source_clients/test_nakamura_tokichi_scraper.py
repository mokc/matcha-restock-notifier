import pytest
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus
from source_clients.nakamura_tokichi_scraper import NakamuraTokichiScraper
from unittest.mock import AsyncMock, Mock


@pytest.fixture
def sr_p1_request():
    with open('tests/fixtures/nakamura_tokichi_fixture_page_1.html') as f:
        return f.read()

@pytest.fixture
def sr_p2_request():
    with open('tests/fixtures/nakamura_tokichi_fixture_page_2.html') as f:
        return f.read()

@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_nk_scraper_get_all_items(
    monkeypatch, sr_p1_request, sr_p2_request
):
    mock_fetch = AsyncMock()
    mock_fetch.side_effect = [sr_p1_request, sr_p2_request]
    monkeypatch.setattr(
        'source_clients.nakamura_tokichi_scraper.NakamuraTokichiScraper.fetch_url',
        mock_fetch
    )

    scraper = NakamuraTokichiScraper(Mock())
    
    all_items = await scraper.scrape()

    assert len(all_items) == 20
    assert '9001332932860' in all_items
    item_9001333031164 = all_items['9001333031164'] # Instock item
    assert item_9001333031164.item.id == '9001333031164'
    assert item_9001333031164.item.brand == Brand.NAKAMURA_TOKICHI
    assert item_9001333031164.item.name == 'Matcha Premium Hatsu-Mukashi “No.2”, 20g Can'
    assert item_9001333031164.url == 'https://global.tokichi.jp/products/bessei-hatsumukashi-matcha-uji-er'
    assert item_9001333031164.stock_status == StockStatus.INSTOCK
    assert item_9001333031164.as_of == '2025-06-12 03:00:00,000'

    item_8012517245180 = all_items['8012517245180'] # Out of stock item
    assert item_8012517245180.item.id == '8012517245180'
    assert item_8012517245180.item.brand == Brand.NAKAMURA_TOKICHI
    assert item_8012517245180.item.name == 'Matcha Ato-Mukashi, 30g Can'
    assert item_8012517245180.url == 'https://global.tokichi.jp/products/mc11'
    assert item_8012517245180.stock_status == StockStatus.OUT_OF_STOCK
    assert item_8012517245180.as_of == '2025-06-12 03:00:00,000'

@pytest.mark.asyncio
async def test_nk_scraper_get_instock_items(
    monkeypatch, sr_p1_request, sr_p2_request
):
    mock_fetch = AsyncMock()
    mock_fetch.side_effect = [sr_p1_request, sr_p2_request]
    monkeypatch.setattr(
        'source_clients.nakamura_tokichi_scraper.NakamuraTokichiScraper.fetch_url',
        mock_fetch
    )

    scraper = NakamuraTokichiScraper(Mock())
    all_items = await scraper.scrape()

    instock_items = {id: item for id, item in all_items.items() if item.stock_status == StockStatus.INSTOCK}
    assert len(instock_items) == 11
    assert '9001333031164' in instock_items
    assert '9001333031164' in instock_items
    assert '9001333162236' in instock_items
    assert '8969846423804' in instock_items
    assert '8969846391036' in instock_items
    assert '8969846358268' in instock_items
    assert '8012517310716' in instock_items
    assert '8012517179644' in instock_items
    assert '8012517474556' in instock_items
    assert '8012517540092' in instock_items
    assert '8012517507324' in instock_items

@pytest.mark.asyncio
async def test_nk_scraper_1_page( monkeypatch, sr_p1_request,):
    """
    Test the scraper when there's only one page of products.
    """
    mock_fetch = AsyncMock()
    mock_fetch.return_value = sr_p1_request
    monkeypatch.setattr(
        'source_clients.nakamura_tokichi_scraper.NakamuraTokichiScraper.fetch_url',
        mock_fetch
    )
    monkeypatch.setattr(
        'source_clients.nakamura_tokichi_scraper.NakamuraTokichiScraper.get_total_pages',
        lambda self, text, soup: 1
    )

    scraper = NakamuraTokichiScraper(Mock())
    all_items = await scraper.scrape()

    assert len(all_items) == 16
    # Items on the second page that shouldn't be present
    assert '8012517376252' not in all_items
    assert '8012517409020' not in all_items
    assert '8812217073916' not in all_items
    assert '8012517146876' not in all_items
    