import pytest
from matcha_notifier.enums import Brand, StockStatus, Website
from matcha_notifier.models import Item, ItemStock
from matcha_notifier.restock_notifier import RestockNotifier
from matcha_notifier.stock_data import StockData
from source_clients.marukyu_koyamaen_scraper import MarukyuKoyamaenScraper
from unittest.mock import AsyncMock, Mock


class Bot:
    def __init__(self):
        pass

    def get_all_channels(self):
        return []

@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()

@pytest.mark.asyncio
async def test_send_discord_stock_updates(
    monkeypatch, mock_session, mock_response, mk_request
):
    mock_response.content = mk_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.scraper.ClientSession', mock_session)
    mock_channel = Mock()
    mock_channel.send = AsyncMock()
    bot = Bot()
    notifier = RestockNotifier(bot, mock_channel)

    scraper = MarukyuKoyamaenScraper(mock_session)
    all_items = await scraper.scrape()

    sd = StockData()
    instock_items, _ = sd.get_stock_changes({Website.MARUKYU_KOYAMAEN: all_items}, {})

    is_notified = await notifier.notify_all_new_restocks(instock_items)

    assert is_notified is True
    mock_channel.send.assert_called_once()
    
    embeds = mock_channel.mock_calls[0][2]['view'].embeds
    assert len(embeds) == 1
    assert embeds[0].title == '🔔 NEW/RESTOCKED ITEMS 🔔'

    description = embeds[0].description
    assert description.startswith('The latest matcha restocks as of')
    assert 'Marukyu Koyamaen Sweetened Matcha – Excellent' in description
    assert 'Marukyu Koyamaen Hojicha Mix' in description
    assert 'Marukyu Koyamaen Matcha Mix' in description

@pytest.mark.asyncio
async def test_no_new_restocks():
    bot = Bot()
    mock_channel = Mock()
    notifier = RestockNotifier(bot, mock_channel)
    instock_items = {}

    resp = await notifier.notify_all_new_restocks(instock_items)

    assert resp is False
