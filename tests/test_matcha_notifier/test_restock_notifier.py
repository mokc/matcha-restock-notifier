import pytest
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.restock_notifier import RestockNotifier
from unittest.mock import AsyncMock, Mock


class Bot:
    def __init__(self):
        pass

    def get_all_channels(self):
        return []

@pytest.mark.asyncio
async def test_send_discord_stock_updates(monkeypatch, caplog):
    mock_channel = Mock()
    mock_channel.send = AsyncMock()
    mock_discord_get = Mock()
    mock_discord_get.return_value = mock_channel

    bot = Bot()
    notifier = RestockNotifier(bot)
    instock_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            }
        }
    }
    monkeypatch.setattr('matcha_notifier.restock_notifier.discord_get', mock_discord_get)

    await notifier.notify_all_restocks(instock_items)
    
    mock_discord_get.assert_called_once()
    assert 'restock-alerts channel connected' in caplog.text
    mock_channel.send.assert_called_once()

@pytest.mark.asyncio
async def test_no_new_restocks(monkeypatch):
    # TODO Change to using Mock so that we can assert with assert_not_called()
    mock_discord_get = Mock()

    bot = Bot()
    notifier = RestockNotifier(bot)
    instock_items = {}
    monkeypatch.setattr('matcha_notifier.restock_notifier.discord_get', mock_discord_get)

    resp = await notifier.notify_all_restocks(instock_items)

    mock_discord_get.assert_not_called()
    assert resp is None

@pytest.mark.asyncio
async def test_restock_channel_not_found(caplog):
    bot = Bot()
    notifier = RestockNotifier(bot)
    notifier.__build_restock_alert = Mock()
    instock_items = {
        Brand.MARUKYU_KOYAMAEN: {
            '1G28200C6': {
                'datetime': '2025-06-12T03:00:00-07:00',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix',
                'url': 'https://example.com/hojicha-mix',
                'stock_status': StockStatus.INSTOCK.value
            }
        }
    }

    await notifier.notify_all_restocks(instock_items)

    assert (
        'Failed to notify on restocks - restock-alerts channel not found' in caplog.text
    )
    notifier.__build_restock_alert.assert_not_called()
