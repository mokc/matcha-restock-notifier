import discord
import logging
from typing import List


logger = logging.getLogger(__name__)

class PaginatorView(discord.ui.View):
    def __init__(
        self,
        channel_id: int,
        embeds: List[discord.Embed],
        timeout: float = 120.0
    ):
        super().__init__(timeout=timeout)
        self.channel_id = channel_id
        self.embeds = embeds
        self.page = 0

        if len(self.embeds) == 1:
            self.clear_items()

        self._apply_footer()
        self._apply_button_states()

    def _apply_footer(self) -> None:
        total = len(self.embeds)
        if total == 1:
            return

        embed = self.embeds[self.page]
        embed.set_footer(text=f'Page {self.page + 1}/{total}')

    def _apply_button_states(self) -> None:
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page >= len(self.embeds) - 1

    async def _show(self, interaction: discord.Interaction) -> None:
        self._apply_footer()
        self._apply_button_states()

        await interaction.response.edit_message(
            embed=self.embeds[self.page], view=self
        )

    @discord.ui.button(emoji='◀️', style=discord.ButtonStyle.secondary)
    async def prev_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        """
        Handle the previous button click.
        """
        if self.page > 0:
            self.page -= 1
            await self._show(interaction)

    @discord.ui.button(emoji='▶️', style=discord.ButtonStyle.secondary)
    async def next_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        """
        Handle the next button click.
        """
        if self.page < len(self.embeds) - 1:
            self.page += 1
            await self._show(interaction)

    async def on_timeout(self) -> None:
        # Disable all buttons when time runs out
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        # Ensure the first page of embed stays visible but with a timeout message
        if self.message and self.message.embeds:
            embed = self.message.embeds[0] if self.message.embeds else None
            if embed and len(self.embeds) > 1:
                embed.set_footer(
                    text='This interaction has timed out. Use the command again to start over.'
                )
                try:
                    await self.message.edit(embed=embed, view=self)
                except discord.HTTPException:
                    logger.error("Paginator view edit failed.")
