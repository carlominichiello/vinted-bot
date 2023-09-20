from discord.ext import commands


class Cog(commands.Cog):
    def __init__(
        self, bot, bot_service, bot_config, database_config, scraper_config
    ) -> None:
        self.bot = bot
        self.bot_service = bot_service
        self.bot_config = bot_config
        self.database_config = database_config
        self.scraper_config = scraper_config
