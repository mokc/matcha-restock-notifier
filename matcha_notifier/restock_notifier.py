import logging
from datetime import datetime
from discord import Color, Embed
from discord.ext.commands import Bot
from discord.utils import get as discord_get
from typing import Dict, Optional
from yaml import safe_load
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

with open('config.yaml') as f:
    config = safe_load(f)

class RestockNotifier:
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def notify_all_restocks(self, instock_items: Dict) -> None:
        """
        Notifies the restock-alerts channel for all new/restocked items.
        """
        if not instock_items:
            return

        restock_channel = discord_get(self.bot.get_all_channels(), name='restock-alerts')
        if not restock_channel:
            logger.warning('Failed to notify on restocks - restock-alerts channel not found')
            return
        
        logger.info('restock-alerts channel connected')
        
        embed = await self.__build_restock_alert(instock_items)

        if embed:
            await restock_channel.send(embed=embed)

    async def __build_restock_alert(self, instock_items: Dict) -> Optional[Embed]:
        """
        Constructs the Embed object relaying the notification for new/restocked
        items.
        """
        if len(instock_items) == 0:
            return None

        # Construct date/time
        now = datetime.now(ZoneInfo('America/Los_Angeles'))
        formatted_time = now.strftime('%B %-d, %-I:%M%p PT')

        # Construct description, which outputs the website and item information
        description = [f'The latest matcha restocks as of {formatted_time}\n']
        for website, items in instock_items.items():
            description.append(f'\n🍵 {website.value} 🍵')
            for item_id, data in items.items():
                description.append(
                    f"\n[✨ {data['brand']} {data['name']}]({data['url']})"
                )

        return Embed(
            title='🔔 NEW/RESTOCKED ITEMS 🔔',
            description=''.join(description),
            color=Color.green()
        )
