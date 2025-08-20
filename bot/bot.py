import asyncio
import discord
import logging
import os
import traceback
from discord import Forbidden, Member
from discord.ext import tasks
from discord.utils import get as discord_get
from matcha_notifier.run import run
from textwrap import dedent
from yaml import safe_load


logger = logging.getLogger(__name__)

with open('config.yaml') as f:
    config = safe_load(f)

class MatchaBot(discord.Bot):
    def __init__(self, **options):
        super().__init__(**options)
        self._poll_started = False
        self._synced = False
        
    async def setup_hook(self) -> None:
        logger.info('SETUP_HOOK RUNNING')
        await self._sync_commands_once()
        
        if not self.stock_poll.is_running():
            self.stock_poll.start()

    async def _sync_commands_once(self) -> None:
        if not self._synced:
            logger.info('SYNCING COMMANDS')
            await self.sync_commands()
            self._synced = True

    async def on_ready(self) -> None:
        """
        This function is a fallback for when _setup_hook doesn't get called.
        This function ensures that only the first on_ready call starts the
        stock polling loop.
        """
        logger.info('ON_READY FIRED')
        if not self._poll_started:
            if not self._synced:
                await self._sync_commands_once()

            try:
                self.stock_poll.start()
                self._poll_started = True
                logger.info('ON_READY: STARTED STOCK_POLL (FALLBACK)')
            except Exception:
                logger.warning('ON_READY: FAILED TO START STOCK_POLL')
        else:
            logger.info('ON_READY: STOCK_POLL ALREADY RUNNING')

    @tasks.loop(seconds=config.get('POLL_INTERVAL', 60), reconnect=True)
    async def stock_poll(self) -> None:
        start = asyncio.get_event_loop().time()
        logger.info('STOCK_POLL STARTED')
        try:
            await asyncio.wait_for(
                run(self), timeout=config.get('POLL_TIMEOUT', 55)
            )
            dur = asyncio.get_event_loop().time() - start
            logger.info(f'STOCK_POLL COMPLETED IN {dur:.2f} SECONDS')
        except asyncio.TimeoutError as e:
            logger.warning('Stock polling timed out')
        
        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f'Stock polling error - {error_message}')
            message = (
                f'An error occurred in stock_polling_loop:\n'
                f'```{error_message[:1900]}```'
            )
            await self._notify_owner(message)

    async def _notify_owner(self, message: str) -> bool:
        owner_id = os.getenv('DISCORD_OWNER_ID')
        if not owner_id:
            return False

        try:
            owner_id = int(owner_id)
            user = await self.fetch_user(owner_id)
            await user.send(message)
        except Exception as dm_error:
            logger.error("Failed to send error DM: %s", traceback.format_exc())
            return False

        return True

    async def on_connect(self):
        logger.info('BOT CONNECTED TO DISCORD GATEWAY')

    async def on_disconnect(self):
        logger.warning('BOT DISCONNECTED')

    async def on_resumed(self):
        logger.warning('BOT SUCCESSFULLY RESUMED CONNECTION')

    async def on_error(self, event, *args, **kwargs):
        logger.error(f'An error occurred in event {event} - {args}')

    async def on_member_join(self, member: Member) -> None:
        """
        Welcome new member to the server in a channel and privately.
        """
        # Send private DM
        try:
            await member.send(dedent(f'''
                Welcome to the server, {member.mention}!

                This server was created to alert friends and family when 
                matcha powder is restocked on a number of websites. With the 
                matcha shortage, I know it\'s been difficult to find and buy 
                matcha so hopefully this server can help!

                You can interact with the bot by using commands under the 
                "commands" button or by typing "/" in the chat. Commands may be 
                used in private messages with the bot or in any channel.

                You\'ll find the latest restocks in the #restock-alerts channel. 
                If you have any questions, feel free to ask in the #general channel 
                or DM Cheryl directly.

                Lastly, don\'t forget to enable push notifications for this 
                server so you don\'t miss the alerts!
                '''
                )
            )
        except Forbidden as e:
            logger.warning(f'Couldn\'t send a DM to {member.display_name} upon joining')

        general_channel = discord_get(member.guild.text_channels, name='general')
        if general_channel:
            try:
                await general_channel.send(
                    f'Everyone welcome {member.mention} to the server! 🎉'
                )
            except Forbidden as e:
                logger.warning(f'Couldn\'t send a message to {general_channel.name} upon {member.display_name} joining')
