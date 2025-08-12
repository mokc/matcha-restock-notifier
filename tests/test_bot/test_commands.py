import bot.commands as commands
import pytest
from matcha_notifier.enums import Website
from matcha_notifier.stock_data import StockData
from source_clients.marukyu_koyamaen_scraper import MarukyuKoyamaenScraper
from unittest.mock import AsyncMock, Mock


@pytest.fixture
def mk_request():
    with open('tests/fixtures/marukyu_koyamaen_fixture.html') as f:
        return f.read()

@pytest.mark.asyncio
async def test_commands_register():
    """
    Test that commands are registered correctly
    """
    bot = Mock()
    commands.register_commands(bot)
    # Test how many times bot.slash command was called
    assert bot.slash_command.call_count == 5
    # Check if the command functions are registered
    funcs = bot.slash_command.call_args_list
    assert funcs[0][1]['name'] == 'subscribe-website'
    assert funcs[1][1]['name'] == 'subscribe-brand'
    assert funcs[2][1]['name'] == 'subscribe-blend'
    assert funcs[3][1]['name'] == 'get-website-instock-items'
    assert funcs[4][1]['name'] == 'get-all-instock-items'

@pytest.mark.asyncio
async def test_get_website_instock_items(monkeypatch, mk_request):
    """
    Test the get_website_instock_items command
    """
    ctx = AsyncMock()
    scraper = MarukyuKoyamaenScraper(session=AsyncMock())
    all_items = {Website.MARUKYU_KOYAMAEN: scraper.parse_products(mk_request)}
    sd = StockData()
    _, new_state = sd.get_stock_changes(all_items, {})
    sd.load_state = AsyncMock(return_value=new_state)
    monkeypatch.setattr('bot.commands.StockData', lambda: sd)
    
    await commands.get_website_instock_items(ctx, website='Marukyu Koyamaen')
    
    embed = ctx.channel.mock_calls[0][2]['embed']
    assert 'Marukyu Koyamaen Sweetened Matcha' in embed.description
    assert 'Marukyu Koyamaen Hojicha Mix' in embed.description
    assert 'Marukyu Koyamaen Matcha Mix' in embed.description
    assert ctx.channel.send.call_count == 1
