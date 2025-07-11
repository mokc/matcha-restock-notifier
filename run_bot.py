import logging
import os
from bot.commands import register_commands
from bot.events import register_events
from discord import ApplicationContext, Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv
from matcha_notifier.run import run


logger = logging.getLogger(__name__)

intents = Intents.default()
intents.members = True
bot = Bot(command_prefix='/', intents=intents)

load_dotenv()
register_events(bot)
register_commands(bot)
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
