import logging
import time

from src.datamodels.transformers import (get_item_from_scraping, item_to_json,
                                         json_items_eq, user_to_json)
from src.scraping.scraper import Scraper

logger = logging.getLogger("scraper")


class Monitor:
    def __init__(self, config):
        self.config = config
        self.scraper = Scraper()

    def run(self, bot_service, database):
        webhooks = bot_service.get_webhooks()
        logger.info(f"Monitoring {len(webhooks)} urls")
        bot_service.on_start(webhooks)
        for webhook, value in webhooks.items():
            urls = self.get_urls_to_scrape(value)
            posts = []
            for url in urls:
                try:
                    posts.extend(self.scraper.get_posts(url))
                except Exception as e:
                    logger.error(f"Error while scraping {url}: {e}")

            new_posts = self.remove_dupes(posts, database)  # new or with a new price

            for catalog_data in new_posts:
                try:
                    item_details, user_data = self.scraper.get_post(catalog_data["url"])
                    item = get_item_from_scraping(catalog_data, item_details, user_data)
                    user = item.user

                    json_item = item_to_json(item)
                    json_user = user_to_json(user)

                    logger.debug(f"Item: {json_item}")
                    logger.debug(f"User: {json_user}")

                    self.on_data(json_item, database.items, database)
                    self.on_data(json_user, database.users, database)

                    json_item["user"] = json_user
                    bot_service.process_item(json_item, webhook)

                    logger.debug(
                        f"Sleeping for {self.config['request_interval']} seconds"
                    )
                    time.sleep(self.config["request_interval"])
                except Exception as e:
                    logger.error(f"Error while scraping {catalog_data['url']}: {e}")

        bot_service.on_finish()
        logger.info(f"Next recheck in {self.config['recheck_interval']} seconds")
        time.sleep(self.config["recheck_interval"])

    def on_data(self, json_data, collection, database):
        return (
            self.on_exists(json_data, collection, database)
            if database.exists(json_data, collection)
            else self.on_not_exists(json_data, collection, database)
        )

    def on_exists(self, json_data, collection, database):
        database.update(json_data, collection)
        return True

    def on_not_exists(self, json_data, collection, database):
        database.insert(json_data, collection)
        return False

    def get_urls_to_scrape(self, webhook_value):
        base_url = webhook_value["url"]
        page_limit = self.config["page_limit"]
        return [f"{base_url}&page={page}" for page in range(1, page_limit + 1)]

    def remove_dupes(self, items, database):
        no_dupes = []
        all_items = list(database.items[1].find({}))
        all_items_ids = [item["vinted_id"] for item in all_items]
        for item in items:
            if item["id"] in all_items_ids:
                db_item = [
                    item_ for item_ in all_items if item_["vinted_id"] == item["id"]
                ][0]
                if db_item["price"] != item["total_item_price"]["amount"]:
                    logger.info(
                        f"Item {item['title']} has a new price: {item['total_item_price']['amount']}€ instead of {db_item['price']}€"
                    )
                    no_dupes.append(item)
            else:
                no_dupes.append(item)
        logger.info(f"Skipping {len(items) - len(no_dupes)} items already in database")
        return no_dupes
