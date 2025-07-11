import asyncio
import logging
import os
import traceback
from typing import Awaitable, Callable
from discord import Forbidden, Member
from discord.ext.commands import Bot
from discord.utils import get as discord_get
from matcha_notifier.run import run


logger = logging.getLogger(__name__)
polling_loop_started = False

def on_ready_handler(bot: Bot) -> Callable[[], Awaitable[None]]:
    async def on_ready() -> None:
        # Prevents creating a new polling loop every time the bot disconnects
        global polling_loop_started
        logger.info(f"Logged in as {bot.user}")

        if not polling_loop_started:
            polling_loop_started = True
            await bot.sync_commands()   # Sync slash commands
            bot.loop.create_task(stock_polling_loop(bot))

    return on_ready

async def stock_polling_loop(bot: Bot) -> None:
    # Ensure the bot is ready before starting the loop
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            await run(bot)
        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f'Stock polling error - {error_message}')

            # Try to DM owner
            try:
                owner_id = os.getenv('DISCORD_OWNER_ID')
                user = await bot.fetch_user(owner_id)
                await user.send(
                    f'An error occurred in stock_polling_loop:\n'
                    f'```{error_message[:1900]}```'
                )
            except Exception as dm_error:
                logger.error("Failed to send error DM: %s", traceback.format_exc())

        await asyncio.sleep(60)

async def on_connect():
    logger.info('BOT CONNECTED TO DISCORD GATEWAY')

async def on_disconnect():
    logger.warning('BOT DISCONNECTED')

async def on_resumed():
    logger.warning('BOT SUCCESSFULLY RESUMED CONNECTION')

async def on_member_join(member: Member) -> None:
    """
    Welcome new member to the server in a channel and privately.
    """
    # Send private DM
    try:
        await member.send(
            f'Welcome to the server, {member.mention}!\n'
            '\n'
            'This server was created to alert friends and family members when '
            'matcha powder is restocked. With the matcha shortage, I know it\'s '
            'been difficult to find and buy matcha so hopefully this server helps!'
        )
    except Forbidden as e:
        logger.warning(f'Couldn\'t send a DM to {member.display_name} upon joining')

    general_channel = discord_get(member.guild.text_channels, name='general')
    if general_channel:
        await general_channel.send(
            f'Everyone welcome {member.mention} to the server! 🎉'
        )

def register_events(bot: Bot) -> None:
    bot.event(on_ready_handler(bot))
    bot.event(on_connect)
    bot.event(on_disconnect)
    bot.event(on_resumed)
    bot.event(on_member_join)