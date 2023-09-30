from src import (
    Config,
    Database,
    Scraper,
    database_config_schema,
    scraper_config_schema,
    setup_logger,
    QueryGenerator,
)
import logging
import time


if __name__ == "__main__":
    scraper_config = Config("./config/scraper.yaml", scraper_config_schema)
    database_config = Config("./config/database.yaml", database_config_schema)

    setup_logger("scraper", scraper_config)
    setup_logger("database", database_config)

    database = Database(database_config)
    scraper = Scraper(scraper_config)

    query_generator = QueryGenerator()
    url = "https://www.vinted.fr/catalog?search_text=&catalog%5B%5D=2051&brand_ids%5B%5D=88"
    params = query_generator.get_query(url)

    start_page = 1

    logger = logging.getLogger("scraper")

    while True:
        items_ids = scraper.scrape_items(**params, start_page=start_page)
        if not items_ids:
            break
        start_page += 1

        no_dupes = database.get_no_dupes(database.items, items_ids)

        logger.info(f"Found {len(no_dupes)} new items for {url}")

        for item in no_dupes:
            json_item, json_user = scraper.scrape_item(item)
            database.items[1].insert_one(json_item)
            database.users[1].insert_one(json_user)
            logger.info(f"Item: {json_item['id']} - {json_item['title']}")
            time.sleep(scraper_config["request_interval"])
