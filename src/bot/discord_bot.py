import logging

import discord
from discord.ext import commands

from src.bot.bot_service import BotService
from src.bot.cogs.database_cog import DatabaseCog
from src.bot.cogs.discord_cog import DiscordCog
from src.bot.cogs.help_cog import HelpCog
from src.bot.cogs.vinted_cog import VintedCog

logger = logging.getLogger("bot")


class DiscordBot:
    cogs = [VintedCog, HelpCog, DatabaseCog, DiscordCog]

    def __init__(self, bot_config, database_config, scraper_config) -> None:
        self.bot_config = bot_config
        self.database_config = database_config
        self.scraper_config = scraper_config

        command_prefix = bot_config["command_prefix"]
        self.bot = commands.Bot(
            command_prefix=command_prefix, intents=discord.Intents.all()
        )
        self.bot_service = BotService(bot_config, database_config, scraper_config)

        self._setup()

    def _setup(self):
        self.bot.remove_command("help")

        @self.bot.event
        async def on_ready():
            logger.info("Bot is ready")
            logger.info(f"Bot name: {self.bot.user.name}")

            await self._setup_cogs()
            await self.bot.change_presence(
                activity=discord.Game(name="Scraping Vinted")
            )

    async def _setup_cogs(self):
        for cog in self.cogs:
            await self.bot.add_cog(
                cog(
                    self.bot,
                    self.bot_service,
                    self.bot_config,
                    self.database_config,
                    self.scraper_config,
                )
            )

    def run(self):
        logger.info("Starting bot...")
        self.bot.run(self.bot_config["token"])
