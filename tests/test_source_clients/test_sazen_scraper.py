import pytest
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus
from source_clients.sazen_scraper import SazenScraper
from unittest.mock import AsyncMock, Mock


@pytest.fixture
def sazen_requests():
    # Ordering of files is important for the test
    files = [
        'tests/fixtures/sazen_fixture.html',
        'tests/fixtures/sazen_matcha_unsui_page_fixture.html',
        'tests/fixtures/sazen_matcha_hatsumukashi_page_fixture.html',
        'tests/fixtures/sazen_matcha_seiro_page_fixture.html',
        'tests/fixtures/sazen_matcha_shimizuoto_page_fixture.html',
        'tests/fixtures/sazen_matcha_chiyo_no_sakae_page_fixture.html',
        'tests/fixtures/sazen_matcha_kin_no_uzu_page_fixture.html',
        'tests/fixtures/sazen_matcha_tenko_page_fixture.html'
    ]
    texts = []
    for f in files:
        with open(f) as file:
            texts.append(file.read())

    return texts

@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_sazen_scraper_instock_items(
    monkeypatch, sazen_requests: list[str]
):
    mock_fetch = AsyncMock()
    mock_fetch.side_effect = sazen_requests
    monkeypatch.setattr('source_clients.sazen_scraper.SazenScraper.fetch_url', mock_fetch)

    scraper = SazenScraper(Mock())
    all_items = await scraper.scrape()

    assert len(all_items) == 7

    cmc007 = all_items['CMC007']
    assert cmc007.item.id == 'CMC007'
    assert cmc007.item.brand == Brand.MARUYASU
    assert cmc007.item.name == 'Matcha Unsui'
    assert cmc007.url == 'https://www.sazentea.com/en/products/p1614-matcha-unsui.html'
    assert cmc007.as_of == '2025-06-12 03:00:00,000'
    assert cmc007.stock_status == StockStatus.INSTOCK

    mtg010 = all_items['MTG010']
    assert mtg010.item.id == 'MTG010'
    assert mtg010.item.brand == Brand.HEKISUIEN
    assert mtg010.item.name == 'Matcha Hatsumukashi'
    assert mtg010.url == 'https://www.sazentea.com/en/products/p200-matcha-hatsumukashi.html'
    assert mtg010.as_of == '2025-06-12 03:00:00,000'
    assert mtg010.stock_status == StockStatus.INSTOCK

    cmc133 = all_items['CMC133']
    assert cmc133.item.id == 'CMC133'
    assert cmc133.item.brand == Brand.MARUYASU
    assert cmc133.item.name == 'Matcha Seiro'
    assert cmc133.url == 'https://www.sazentea.com/en/products/p1639-matcha-seiro.html'
    assert cmc133.as_of == '2025-06-12 03:00:00,000'
    assert cmc133.stock_status == StockStatus.INSTOCK

    assert 'CMC134' in all_items
    assert 'CMM001' in all_items
    assert 'MTG009' in all_items
    assert 'MTG005' in all_items
