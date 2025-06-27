import asyncio
import discord
import logging
import os
import traceback
from dotenv import load_dotenv
from matcha_notifier import run


logger = logging.getLogger(__name__)

load_dotenv()
intents = discord.Intents.default()
bot = discord.ext.commands.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(stock_polling_loop(bot))

async def stock_polling_loop(bot: discord.ext.commands.Bot):
    # Ensure the bot is ready before starting the loop
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            await run()
        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f'Error in stock polling loop - {error_message}')

            # Try to DM owner
            try:
                owner_id = os.getenv('DISCORD_OWNER_ID')
                user = await bot.fetch_user(owner_id)
                await user.send(f"⚠️ An error occurred in stock_polling_loop:\n```{error_message[:1900]}```")
            except Exception as dm_error:
                logger.error("Failed to send error DM: %s", traceback.format_exc())
        
        await asyncio.sleep(60)
