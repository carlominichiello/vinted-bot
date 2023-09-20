import logging

from discord.ext import commands

from src.bot.cogs.cog import Cog
from src.database import Database

database_logger = logging.getLogger("database")


class DatabaseCog(Cog):
    """
    Database commands
    """

    @commands.command()
    async def clear_db(self, ctx):
        """
        Clear the database
        Usage: clear_db
        """
        database = Database(self.database_config)
        database.reset()
        await ctx.send(f"{ctx.author.mention} - **Database cleared!**")
        database_logger.info(f"Database cleared")
