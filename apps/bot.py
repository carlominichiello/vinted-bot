import argparse

from src import DiscordBot
from src.configs.config import Config
from src.configs.schemas import (bot_config_schema, database_config_schema,
                                 scraper_config_schema)
from src.logger.logger import setup as setup_logger


def parse_arguments():
    parser = argparse.ArgumentParser(description="Vinted Bot")
    parser.add_argument(
        "--bot-config",
        type=str,
        default="./config/bot.yaml",
        help="Path to the bot config file",
    )
    parser.add_argument(
        "--database-config",
        type=str,
        default="./config/database.yaml",
        help="Path to the database config file",
    )
    parser.add_argument(
        "--scraper-config",
        type=str,
        default="./config/scraper.yaml",
        help="Path to the scraper config file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    bot_config = Config(args.bot_config, bot_config_schema)
    database_config = Config(args.database_config, database_config_schema)
    scraper_config = Config(args.scraper_config, scraper_config_schema)

    setup_logger("bot", bot_config)
    setup_logger("database", bot_config)

    bot = DiscordBot(bot_config, database_config, scraper_config)
    bot.run()
