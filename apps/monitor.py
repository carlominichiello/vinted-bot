import argparse

from src import (
    BotService,
    Config,
    Database,
    Monitor,
    bot_config_schema,
    database_config_schema,
    scraper_config_schema,
    setup_logger,
)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Vinted Scraper")
    parser.add_argument(
        "--scraper-config",
        type=str,
        default="./config/scraper.yaml",
        help="Path to the config file",
    )
    parser.add_argument(
        "--database-config",
        type=str,
        default="./config/database.yaml",
        help="Path to the config file",
    )
    parser.add_argument(
        "--bot-config",
        type=str,
        default="./config/bot.yaml",
        help="Path to the config file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    scraper_config = Config(args.scraper_config, scraper_config_schema)
    database_config = Config(args.database_config, database_config_schema)
    bot_config = Config(args.bot_config, bot_config_schema)

    setup_logger("scraper", scraper_config)
    setup_logger("database", database_config)
    setup_logger("bot", bot_config)

    database = Database(database_config)
    monitor = Monitor(scraper_config)
    bot_service = BotService(bot_config, database_config, scraper_config)

    while True:
        monitor.run_watch(bot_service, database)
        monitor.run_background_scraping(bot_service, database)
