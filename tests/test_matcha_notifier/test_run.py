import json
import logging
import pytest
from freezegun import freeze_time
from matcha_notifier.enums import Brand, StockStatus
from matcha_notifier.run import run
from pathlib import Path


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
    discord_bot = Bot()

    await run(discord_bot)
    
    test_state = 'test_state.json'
    if Path(test_state).exists():
        with open(test_state) as f:
            state = json.load(f)

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