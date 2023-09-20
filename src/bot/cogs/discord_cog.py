import logging

from discord.ext import commands

from src.bot.cogs.cog import Cog

logger = logging.getLogger("bot")


class DiscordCog(Cog):
    """
    Discord commands
    """

    @commands.command()
    async def clear_channel(self, ctx, amount=1000):
        """
        Clears the channel of all messages
        Usage: `clear_channel [amount=1000]`
        """
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{ctx.author.mention} - **✔️ Successfully cleared channel!**")
        logger.info(f"Channel {ctx.channel.name} cleared")
