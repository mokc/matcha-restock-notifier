import logging
from datetime import datetime
from discord import Color, DMChannel, Embed, Forbidden, TextChannel
from discord.ext.commands import Bot
from discord.utils import get as discord_get
from typing import Dict, Optional, Union
from yaml import safe_load
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

with open('config.yaml') as f:
    config = safe_load(f)

class RestockNotifier:
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def notify_all_new_restocks(self, instock_items: Dict) -> bool:
        """
        Notifies the restock-alerts channel for all new/restocked items.
        """
        if not instock_items:
            return False

        restock_channel = discord_get(self.bot.get_all_channels(), name='restock-alerts')
        if not restock_channel:
            logger.warning('Failed to notify on restocks - restock-alerts channel not found')
            return False
        
        logger.info('restock-alerts channel connected')
        
        embed = self.__build_new_restocks_alert(instock_items)

        if embed:
            try:
                await restock_channel.send(embed=embed)
            except Exception as e:
                logger.error(f'Failed to send restock notification: {e}')
                return False
            
        return True

    def __build_new_restocks_alert(self, instock_items: Dict) -> Optional[Embed]:
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
                    f"\n[✨ {data.item.brand.value} {data.item.name}]({data.url})"
                )

        return Embed(
            title='🔔 NEW/RESTOCKED ITEMS 🔔',
            description=''.join(description),
            color=Color.green()
        )

    async def notify_instock_items(self, instock_items: Dict, channel: Union[TextChannel, DMChannel]) -> bool:
        """
        Notifies the member for instock items.
        """
        if not instock_items:
            return False

        embed = self.__build_instock_alert(instock_items)
        try:
            await channel.send(embed=embed)
        except Forbidden as e:
            logger.warning(f'Unable to DM {channel} for in-stock items')
            return False
        
        return True

    def __build_instock_alert(self, instock_items: Dict) -> Optional[Embed]:
        """
        Constructs the Embed object relaying the notification for in-stock items.
        """
        if len(instock_items) == 0:
            return None
        
        response = []
        for website, items in instock_items.items():
            response.append(f'\n🍵 {website.value} 🍵')
            for item_id, data in items.items():
                response.append(
                    f"\n[✨ {data.item.brand.value} {data.item.name}]({data.url})"
                )
                
        return Embed(
            title='🔔 ITEMS IN STOCK 🔔',
            description=''.join(response),
            color=Color.green()
        )