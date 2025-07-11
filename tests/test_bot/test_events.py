import asyncio
import json
import pytest
from bot.events import (
    on_connect, on_disconnect, on_ready_handler, on_resumed,
    stock_polling_loop
)
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock


@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()

@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_bot_stock_polling_success(
    monkeypatch, mock_session, mock_response, mk_request
):      
    mock_bot = Mock()
    mock_bot.wait_until_ready = AsyncMock()
    mock_bot.is_closed.side_effect = [False, True]
    mock_bot.get_all_channels = Mock(return_value=[])
    mock_response.content = mk_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.run.ClientSession', mock_session)
    monkeypatch.setattr(asyncio, 'sleep', AsyncMock())  # Avoid actual sleep calls

    await stock_polling_loop(mock_bot)
    
    test_state = 'test_state.json'
    if Path(test_state).exists():
        with open(test_state) as f:
            state = json.load(f)

    mock_bot.wait_until_ready.assert_awaited_once()
    assert len(state) == 1
    mk = state[Brand.MARUKYU_KOYAMAEN.value]
    assert len(mk) == 51
    instock_items = {item : data for item, data in mk.items() if data['stock_status'] == 'instock'}
    assert len(instock_items) == 3
    assert instock_items == {
        '1186000CC-1C83000CC': {
            'datetime': '2025-06-12T03:00:00-07:00',
            'brand': 'Marukyu Koyamaen',
            'name': 'Sweetened Matcha – Excellent',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
            'stock_status': StockStatus.INSTOCK.value
        },
        '1G28200C6': {
            'datetime': '2025-06-12T03:00:00-07:00',
            'brand': 'Marukyu Koyamaen',
            'name': 'Hojicha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
            'stock_status': StockStatus.INSTOCK.value
        },
        '1G9D000CC-1GAD200C6': {
            'datetime': '2025-06-12T03:00:00-07:00',
            'brand': 'Marukyu Koyamaen',
            'name': 'Matcha Mix',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
            'stock_status': StockStatus.INSTOCK.value
            }
        }

@pytest.mark.asyncio
async def test_bot_on_ready_multiple_polling_loop(monkeypatch):
    mock_bot = AsyncMock()
    mock_bot.wait_until_ready = AsyncMock()
    mock_bot.is_closed.return_value = False
    mock_bot.loop.create_task = AsyncMock()

    monkeypatch.setattr('bot.events.stock_polling_loop', AsyncMock())

    # Call on_ready_handler twice to simulate multiple calls
    await on_ready_handler(mock_bot)()
    await on_ready_handler(mock_bot)()

    mock_bot.sync_commands.assert_awaited_once()
    mock_bot.loop.create_task.assert_called_once()

@pytest.mark.asyncio
async def test_bot_on_connect(caplog):
    await on_connect()

    assert 'BOT CONNECTED TO DISCORD GATEWAY' in caplog.text

@pytest.mark.asyncio
async def test_bot_on_disconnect(caplog):
    await on_disconnect()

    assert 'BOT DISCONNECTED' in caplog.text

@pytest.mark.asyncio
async def test_bot_on_resumed(caplog):
    await on_resumed()

    assert 'BOT SUCCESSFULLY RESUMED CONNECTION' in caplog.text

@pytest.mark.asyncio
async def test_bot_member_joins():
    # TODO
    pass