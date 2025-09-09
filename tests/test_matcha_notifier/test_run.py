import asyncio
import json
import logging
import pytest
from freezegun import freeze_time
from matcha_notifier.enums import Brand, Website
from matcha_notifier.run import run
from pathlib import Path
from source_clients.marukyu_koyamaen_scraper import MarukyuKoyamaenScraper
from unittest.mock import AsyncMock, Mock


logger = logging.getLogger(__name__)

@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()


class Bot:
    def __init__(self):
        pass

    def get_all_channels(self):
        return []


@pytest.mark.asyncio
@freeze_time("2025-06-12 17:00:00", tz_offset=-7)
async def test_run(monkeypatch, mock_session, mock_response, mk_request, caplog):
    class StopLoop(Exception):
        pass

    # Counter to track how many times asyncio.sleep is called
    counter = 0
    async def mock_sleep(seconds):
        nonlocal counter
        counter += 1
        if counter >= 2:
            raise StopLoop

    # Patch out sleep and Event.wait
    monkeypatch.setattr('matcha_notifier.run.asyncio.sleep', mock_sleep)
    monkeypatch.setattr('matcha_notifier.run.asyncio.Event.wait', AsyncMock())

    # Patch network call
    mock_response.content = mk_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.run.ClientSession', mock_session)

    # Patch Discord
    mock_channel = Mock()
    mock_channel.send = AsyncMock()
    mock_discord_get = Mock()
    mock_discord_get.return_value = mock_channel
    monkeypatch.setattr('matcha_notifier.run.discord_get', mock_discord_get)

    # Patch just one source for faster testing
    monkeypatch.setattr('matcha_notifier.run.SOURCE_MAPPER', {
        Website.MARUKYU_KOYAMAEN: MarukyuKoyamaenScraper
    })

    # Bot
    discord_bot = Bot()

    # Run main loop and break out using mock_sleep
    try:
        await run(discord_bot)

        # Give any remaining tasks a chance to run (like send_alerts)
        pending = [t for t in asyncio.all_tasks() if not t.done()]
        for t in pending:
            if t.get_coro().__name__ == 'send_alerts':
                await asyncio.wait_for(t, timeout=1)

    except StopLoop:
        pass

    # Check log output
    assert 'restock-alerts channel connected' in caplog.text
    assert 'NEW INSTOCK ITEMS' in caplog.text

    # Load and verify saved state
    test_state_path = Path('test_state.json')
    assert test_state_path.exists()

    with open(test_state_path) as f:
        state = json.load(f)

    assert len(state) == 1
    marukyu_data = state[Website.MARUKYU_KOYAMAEN.value]
    assert len(marukyu_data) == 51

    instock_items = {
        item_id: data for item_id, data in marukyu_data.items()
        if data['stock_status'] == 'instock'
    }

    assert len(instock_items) == 3
    assert instock_items == {
        '1186000CC-1C83000CC': {
            'item': {
                'id': '1186000CC-1C83000CC',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Sweetened Matcha – Excellent'
            },
            'as_of': '2025-06-12 03:00:00,000',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc',
            'stock_status': 'instock'
        },
        '1G28200C6': {
            'item': {
                'id': '1G28200C6',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix'
            },
            'as_of': '2025-06-12 03:00:00,000',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
            'stock_status': 'instock'
        },
        '1G9D000CC-1GAD200C6': {
            'item': {
                'id': '1G9D000CC-1GAD200C6',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix'
            },
            'as_of': '2025-06-12 03:00:00,000',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
            'stock_status': 'instock'
        }
    }

@pytest.mark.asyncio
async def test_restock_channel_not_found(
    monkeypatch, mock_response, mock_session, mk_request, caplog
):
    mock_response.content = mk_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.run.ClientSession', mock_session)
    mock_discord_get = Mock()
    mock_discord_get.return_value = []
    monkeypatch.setattr('matcha_notifier.run.discord_get', mock_discord_get)
    monkeypatch.setattr('matcha_notifier.run.SOURCE_MAPPER', {
        Website.MARUKYU_KOYAMAEN: MarukyuKoyamaenScraper
    })
    monkeypatch.setattr(asyncio.Event, 'wait', lambda self: asyncio.sleep(0))
    
    discord_bot = Bot()

    await run(discord_bot)

    assert (
        'Failed to notify on restocks - restock-alerts channel not found' in caplog.text
    )
