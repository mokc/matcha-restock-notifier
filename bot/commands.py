from discord import ApplicationContext
from discord.ext.commands import Bot


def register_commands(bot: Bot) -> None:
    @bot.slash_command(name='subscribe-website', description='Subscribe to alerts for a website', guild_ids=['1387151602288165056'])
    async def subscribe_website(ctx: ApplicationContext, site: str) -> None:
        # TODO Add options to give hints to users about subscribe options
        await ctx.respond('SUBSCRIBING')

    @bot.slash_command(name='subscribe-brand', description='Subscribe to alerts for a brand', guild_ids=['1387151602288165056'])
    async def subscribe_brand(ctx: ApplicationContext, brand: str) -> None:
        # TODO
        await ctx.respond('SUBSCRIBING')

    @bot.slash_command(name='subscribe-blend', description='Subscribe to alerts for a blend', guild_ids=['1387151602288165056'])
    async def subscribe_blend(ctx: ApplicationContext, blend: str) -> None:
        # TODO
        await ctx.respond('SUBSCRIBING')
