import asyncio
import json
import pytest
from bot.bot import MatchaBot
from discord import Intents
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus, Website
from pathlib import Path
from source_clients.marukyu_koyamaen_scraper import MarukyuKoyamaenScraper
from unittest.mock import AsyncMock, Mock


@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()

@pytest.fixture
def mock_bot():
    intents = Intents.default()
    intents.members = True
    bot = MatchaBot(command_prefix='/', intents=intents)
    return bot

@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_bot_run_success(
    monkeypatch, mock_bot, mock_session, mock_response, mk_request
):
    class StopLoop(Exception):
        pass

    # Counter to track how many times asyncio.sleep is called
    counter = 0
    async def mock_sleep(seconds):
        nonlocal counter
        counter += 1
        if counter >= 2:
            raise StopLoop
        
    monkeypatch.setattr('matcha_notifier.run.asyncio.sleep', mock_sleep)
    monkeypatch.setattr('matcha_notifier.run.asyncio.Event.wait', AsyncMock())

    mock_bot.get_all_channels = Mock(return_value=[])
    mock_response.content = mk_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.run.ClientSession', mock_session)
    mock_notify_all_new_restocks = AsyncMock(return_value=True)
    monkeypatch.setattr(
        'matcha_notifier.run.RestockNotifier.notify_all_new_restocks',
        mock_notify_all_new_restocks
    )
    monkeypatch.setattr('matcha_notifier.run.SOURCE_MAPPER', {
        Website.MARUKYU_KOYAMAEN: MarukyuKoyamaenScraper
    })
    mock_channel = Mock()
    mock_channel.send = AsyncMock()
    mock_discord_get = Mock()
    mock_discord_get.return_value = mock_channel
    monkeypatch.setattr('matcha_notifier.run.discord_get', mock_discord_get)

    try:
        await mock_bot.on_ready()
        await asyncio.wait_for(mock_bot._run_task, timeout=4)

        # Give any remaining tasks a chance to run (like send_alerts)
        pending = [t for t in asyncio.all_tasks() if not t.done()]
        for t in pending:
            if t.get_coro().__name__ == 'send_alerts':
                await asyncio.wait_for(t, timeout=1)

    except StopLoop:
        pass

    test_state = 'test_state.json'
    if Path(test_state).exists():
        with open(test_state) as f:
            state = json.load(f)

    assert len(state) == 1
    mk = state[Brand.MARUKYU_KOYAMAEN.value]
    assert len(mk) == 51
    # Parse instock items from state
    instock_items = {item : data for item, data in mk.items() if data['stock_status'] == 'instock'}
    assert len(instock_items) == 3
    assert instock_items == {
        '1186000CC-1C83000CC': {
            'item': {
                'id': '1186000CC-1C83000CC',
                'brand': 'Marukyu Koyamaen',
                'name': 'Sweetened Matcha – Excellent'
            },
            'as_of': '2025-06-12 03:00:00,000',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
            'stock_status': StockStatus.INSTOCK.value
        },
        '1G28200C6': {
            'item': {
                'id': '1G28200C6',
                'brand': 'Marukyu Koyamaen',
                'name': 'Hojicha Mix'
            },
            'as_of': '2025-06-12 03:00:00,000',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
            'stock_status': StockStatus.INSTOCK.value
        },
        '1G9D000CC-1GAD200C6': {
            'item': {
                'id': '1G9D000CC-1GAD200C6',
                'brand': 'Marukyu Koyamaen',
                'name': 'Matcha Mix'
            },
            'as_of': '2025-06-12 03:00:00,000',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
            'stock_status': StockStatus.INSTOCK.value
            }
        }

@pytest.mark.asyncio
async def test_bot_on_ready_multiple_polling_loop(monkeypatch, mock_bot):
    """
    Ensure that on disconnects, the stock polling loop isn't called multiple
    times.
    """
    # Call on_ready twice to simulate multiple calls
    await mock_bot.on_ready()
    await mock_bot.on_ready()

    assert mock_bot._run_task is not None

    all_tasks = asyncio.all_tasks()
    assert len(all_tasks) == 2  # Only the test task and the first run task
    names = {'_run_wrapper', 'test_bot_on_ready_multiple_polling_loop'}
    for task in all_tasks:
        assert task.get_coro().__name__ in names

@pytest.mark.asyncio
async def test_bot_on_connect(caplog, mock_bot):
    await mock_bot.on_connect()

    assert 'BOT CONNECTED TO DISCORD GATEWAY' in caplog.text

@pytest.mark.asyncio
async def test_bot_on_disconnect(caplog, mock_bot):
    await mock_bot.on_disconnect()

    assert 'BOT DISCONNECTED' in caplog.text

@pytest.mark.asyncio
async def test_bot_on_resumed(caplog, mock_bot):
    await mock_bot.on_resumed()

    assert 'BOT SUCCESSFULLY RESUMED CONNECTION' in caplog.text

@pytest.mark.asyncio
async def test_bot_member_joins(monkeypatch, mock_bot):
    mock_member = Mock()
    mock_member.send = AsyncMock()
    mock_member.id = 123456789
    mock_member.name = 'TestUser'

    mock_get = Mock()
    mock_channel = Mock
    mock_channel.send = AsyncMock()
    mock_get.return_value = mock_channel
    monkeypatch.setattr('bot.bot.discord_get', mock_get)

    await mock_bot.on_member_join(mock_member)

    mock_member.send.assert_awaited_once()
    mock_channel.send.assert_awaited_once()
