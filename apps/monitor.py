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
    parser.add_argument(
        "--save-to-db",
        action="store_true",
        help="Save data to database",
    )
    parser.add_argument(
        "--run-random-scraping",
        action="store_true",
        help="Run random scraping",
    )
    parser.add_argument(
        "--run-background-scraping",
        action="store_true",
        help="Run background scraping",
    )
    parser.add_argument(
        "--run-watch",
        action="store_true",
        help="Run watch",
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

    database = Database(database_config, args.save_to_db)
    monitor = Monitor(scraper_config)
    bot_service = BotService(bot_config, database_config, scraper_config)

    if args.run_random_scraping:
        monitor.run_background_scraping(bot_service, database)
    if args.run_background_scraping:
        monitor.run_random_scraping(bot_service, database)
    if args.run_watch:
        while True:
            monitor.run_watch(bot_service, database)
