import logging
import os
from bot.bot import MatchaBot
from bot.commands import register_commands
from discord import Intents
from dotenv import load_dotenv
from matcha_notifier.run import run


logger = logging.getLogger(__name__)

intents = Intents.default()
intents.members = True
bot = MatchaBot(command_prefix='/', intents=intents)

load_dotenv()
register_commands(bot)
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
