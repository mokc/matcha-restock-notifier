import logging
import traceback
from discord import ApplicationContext, Option
from discord.ext.commands import Bot
from matcha_notifier.enums import Website
from matcha_notifier.restock_notifier import RestockNotifier
from matcha_notifier.stock_data import StockData


logger = logging.getLogger(__name__)

WEBSITE_CHOICES = [w.value for w in Website]

async def subscribe_website(ctx: ApplicationContext, site: str) -> None:
    # TODO Add options to give hints to users about subscribe options
    await ctx.respond('NOT YET IMPLEMENTED')

async def subscribe_brand(ctx: ApplicationContext, brand: str) -> None:
    # TODO
    await ctx.respond('NOT YET IMPLEMENTED')

async def subscribe_blend(ctx: ApplicationContext, blend: str) -> None:
    # TODO
    await ctx.respond('NOT YET IMPLEMENTED')

async def get_website_instock_items(
    ctx: ApplicationContext,
    website: Option(str, choices=WEBSITE_CHOICES)  # type: ignore
) -> None:
    await ctx.respond(f'FETCHING IN STOCK ITEMS FOR {website.upper()}')
    
    sd = StockData()
    site = Website(website)
    try:
        state = await sd.load_state()
        instock_items = sd.get_website_instock_items(site, state)
        if not instock_items:
            await ctx.respond(f'No items in stock for {website}.')

        rs = RestockNotifier(ctx.bot)
        await rs.notify_instock_items(instock_items, ctx.channel)
    except Exception as e:
        error_message = traceback.format_exc()
        logger.error(f'Error fetching in stock items for {website}: {error_message}')
        await ctx.respond(f'Error fetching in stock items for {website}. Please try again later.')

async def get_all_instock_items(ctx: ApplicationContext) -> None:
    await ctx.respond('FETCHING ALL IN STOCK ITEMS')
    
    try:
        all_instock_items = await StockData().get_all_instock_items()
        if not all_instock_items:
            await ctx.respond(f'No items in stock.')
        
        rs = RestockNotifier(ctx.bot)
        await rs.notify_instock_items(all_instock_items, ctx.channel)
    except Exception as e:
        error_message = traceback.format_exc()
        logger.error(f'Error fetching all in stock items: {error_message}')
        await ctx.respond('Error fetching all in stock items. Please try again later.')

        logger.error(f'Error fetching all in stock items: {e}')
        await ctx.respond('Error fetching all in stock items. Please try again later.')


def register_commands(bot: Bot) -> None:
    bot.slash_command(name='subscribe-website', description='Subscribe to alerts for a website')(subscribe_website)
    bot.slash_command(name='subscribe-brand', description='Subscribe to alerts for a brand')(subscribe_brand)
    bot.slash_command(name='subscribe-blend', description='Subscribe to alerts for a blend')(subscribe_blend)
    bot.slash_command(name='get-website-instock-items', description='Get all items in stock for a website')(get_website_instock_items)
    bot.slash_command(name='get-all-instock-items', description='Get all items in stock')(get_all_instock_items)
