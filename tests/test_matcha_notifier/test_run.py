import json
import logging
import pytest
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus, Website
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
async def test_run(monkeypatch, mock_session, mock_response, mk_request):
    mock_response.content = mk_request
    mock_session.get = lambda *args, **kwargs: mock_response
    monkeypatch.setattr('matcha_notifier.run.ClientSession', mock_session)
    mock_channel = Mock()
    mock_channel.send = AsyncMock()
    mock_discord_get = Mock()
    mock_discord_get.return_value = mock_channel
    monkeypatch.setattr('matcha_notifier.restock_notifier.discord_get', mock_discord_get)
    monkeypatch.setattr('matcha_notifier.scraper.SOURCE_MAPPER', {
        Website.MARUKYU_KOYAMAEN: MarukyuKoyamaenScraper
    })
    
    discord_bot = Bot()

    await run(discord_bot)
    
    test_state = 'test_state.json'
    if Path(test_state).exists():
        with open(test_state) as f:
            state = json.load(f)

    assert len(state) == 1
    mk = state[Website.MARUKYU_KOYAMAEN.value]
    assert len(mk) == 51
    # Parse instock items from state
    instock_items = {item : data for item, data in mk.items() if data['stock_status'] == 'instock'}
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
            'stock_status': StockStatus.INSTOCK.value
        },
        '1G28200C6': {
            'item': {
                'id': '1G28200C6',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Hojicha Mix'
            },
            'as_of': '2025-06-12 03:00:00,000',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g28200c6',
            'stock_status': StockStatus.INSTOCK.value
        },
        '1G9D000CC-1GAD200C6': {
            'item': {
                'id': '1G9D000CC-1GAD200C6',
                'brand': Brand.MARUKYU_KOYAMAEN.value,
                'name': 'Matcha Mix'
            },
            'as_of': '2025-06-12 03:00:00,000',
            'url': 'https://www.marukyu-koyamaen.co.jp/english/shop/products/1g9d000cc',
            'stock_status': StockStatus.INSTOCK.value
            }
        }
