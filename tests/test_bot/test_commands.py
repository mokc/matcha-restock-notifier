import pytest
from bot.commands import register_commands
from unittest.mock import Mock


@pytest.mark.asyncio
async def test_commands_register():
    """
    Test that commands are registered correctly
    """
    bot = Mock()
    register_commands(bot)
    # Test how many times bot.slash command was called
    assert bot.slash_command.call_count == 4
    # Check if the command functions are registered
    funcs = bot.slash_command.call_args_list
    assert funcs[0][1]['name'] == 'subscribe-website'
    assert funcs[1][1]['name'] == 'subscribe-brand'
    assert funcs[2][1]['name'] == 'subscribe-blend'
    assert funcs[3][1]['name'] == 'get-website-instock-items'
