from discord import ApplicationContext, Option
from discord.ext.commands import Bot
from matcha_notifier.enums import Website
from matcha_notifier.restock_notifier import RestockNotifier
from matcha_notifier.stock_data import StockData


def register_commands(bot: Bot) -> None:
    @bot.slash_command(name='subscribe-website', description='Subscribe to alerts for a website', guild_ids=['1387151602288165056'])
    async def subscribe_website(ctx: ApplicationContext, site: str) -> None:
        # TODO Add options to give hints to users about subscribe options
        await ctx.respond('SUBSCRIBING')

    @bot.slash_command(name='subscribe-brand', description='Subscribe to alerts for a brand')
    async def subscribe_brand(ctx: ApplicationContext, brand: str) -> None:
        # TODO
        await ctx.respond('SUBSCRIBING')

    @bot.slash_command(name='subscribe-blend', description='Subscribe to alerts for a blend')
    async def subscribe_blend(ctx: ApplicationContext, blend: str) -> None:
        # TODO
        await ctx.respond('SUBSCRIBING')

    @bot.slash_command(name='get-website-instock-items', description='Get all items in stock for a website')
    async def get_website_instock_items(
        ctx: ApplicationContext,
        website: Option(str, choices=['Marukyu Koyamaen'])  # type: ignore
    ) -> None:
        await ctx.respond('FETCHING IN STOCK ITEMS')
        
        sd = StockData()
        state = sd.load_state()
        instock_items = sd.get_website_instock_items(Website(website), state)
        rs = RestockNotifier(bot)
        await rs.notify_instock_items(instock_items, ctx.channel)
