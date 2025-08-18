import logging
from datetime import datetime
from discord import Color, DMChannel, Embed, Forbidden, TextChannel
from discord.ext.commands import Bot
from matcha_notifier.enums import Brand, Website
from typing import Dict, List, Optional, Union
from views.paginator_view import PaginatorView
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

class RestockNotifier:
    def __init__(self, bot: Bot, channel: Union[TextChannel, DMChannel]):
        self.bot = bot
        self.channel = channel
        self.embed_desc_limit = 4096
        self.embed_line_limit = 15

    async def notify_all_new_restocks(
        self, instock_items: Dict[Website, Dict]
    ) -> bool:
        """
        Notifies the channel for all new/restocked items.
        """
        if not instock_items:
            return False

        # Construct date/time
        now = datetime.now(ZoneInfo('America/Los_Angeles'))
        formatted_time = now.strftime('%B %-d, %-I:%M%p PT')

        # Construct description, which outputs the website and item information
        caption = f'The latest matcha restocks as of {formatted_time}\n'
        embeds = self._build_instock_alert(
            '🔔 NEW/RESTOCKED ITEMS 🔔',
            instock_items,
            caption=caption
        )

        if embeds:
            view = PaginatorView(self.channel.id, embeds, timeout=120.0)
        
            try:
                await self.channel.send(embed=embeds[0], view=view)
            except Exception as e:
                logger.error(f'Failed to send restock notification: {e}')
                return False
            
        return True

    def _build_instock_alert(
        self, title: str, instock_items: Dict[Website, Dict], caption: str = ''
    ) -> Optional[Embed]:
        """
        Constructs the Embed objects to relay notifications for in-stock items.
        """
        if len(instock_items) == 0:
            return None
                
        # Construct embeds, which describes the website and item information
        data_chunks = self._chunk_lines_by_limit(instock_items, caption)
        
        embeds = []
        for chunk in data_chunks:
            embed = Embed(
                title=title,
                description=chunk,
                color=Color.green()
            )
            embeds.append(embed)

        return embeds
 
    def _chunk_lines_by_limit(
        self, instock_items: Dict[Website, Dict], caption: str
    ) -> List[str]:
        if not instock_items:
            return []

        chunk, chunks = [caption], []
        length = 0
        for website, items in instock_items.items():
            website_line = f'\n🍵 {website.value} 🍵'
            length = self._build_description_chunk(
                website_line, chunk, chunks, length
            )

            for item_id, data in items.items():
                brand = data.item.brand
                if brand == Brand.UNKNOWN:
                    brand = ''
                    brand_name_txt = f'{data.item.name}'
                else:
                    brand_name_txt = f'{brand.value} {data.item.name}'

                item_line = f"\n[✨ {brand_name_txt}]({data.url})"
                length = self._build_description_chunk(
                    item_line, chunk, chunks, length
                )

            length = self._build_description_chunk(
                '\n', chunk, chunks, length
            )

        if chunk:
            chunks.append(''.join(chunk))

        return chunks
        
    def _build_description_chunk(
        self, line: str, chunk: List[str], chunks: List[str], chunk_len: int
    ) -> int:
        """
        Append line to text chunk if space is available. Otherwise, append the
        text chunk into the overall text chunks. Returns the current chunk's
        length.
        """
        # Append chunk to chunks if adding current line exceeds char limit
        if (
            chunk_len + len(line) > self.embed_desc_limit
            or len(chunk) >= self.embed_line_limit
        ):
            chunks.append(''.join(chunk))
            chunk.clear()
            chunk_len = len(chunk)

        chunk.append(line)
        return chunk_len + len(line)

    def _parse_instock_items(
        self, instock_items: Dict, data_chunks: List[str], title: str
    ) -> None:
        for website, items in instock_items.items():
            data_chunks.append(f'\n🍵 {website.value} 🍵')
            for item_id, data in items.items():
                brand = data.item.brand
                if brand == Brand.UNKNOWN:
                    brand = ''
                    brand_name_txt = f'{data.item.name}'
                else:
                    brand_name_txt = f'{brand.value} {data.item.name}'

                data_chunks.append(
                    f"\n[✨ {brand_name_txt}]({data.url})"
                )
            data_chunks.append('\n')

        return Embed(
            title=title,
            description=''.join(data_chunks),
            color=Color.green()
        )

    async def notify_instock_items(
        self,
        instock_items: Dict[Website, Dict]
    ) -> bool:
        """
        Notifies the user of instock items.
        """
        if not instock_items:
            return False

        embeds = self._build_instock_alert('🔔 ITEMS IN STOCK 🔔', instock_items)
        if embeds:
            view = PaginatorView(self.channel.id, embeds, timeout=120.0)

            try:
                await self.channel.send(embed=embeds[0], view=view)
            except Forbidden as e:
                logger.warning(f'Unable to DM {self.channel} for in-stock items')
                return False
        
        return True
