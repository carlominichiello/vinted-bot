import logging
import requests
import time

from src.scraping.scraper import Scraper

logger = logging.getLogger("scraper")


class Monitor:
    def __init__(self, config):
        self._config = config
        self._scraper = Scraper(config)

    def run(self, bot_service, database):
        webhooks = bot_service.get_webhooks()
        logger.info(f"Monitoring {len(webhooks)} urls")
        bot_service.on_start(webhooks)

        for webhook, value in webhooks.items():
            self._process_webhook(webhook, value, bot_service, database)

        bot_service.on_finish()
        logger.info(f"Next recheck in {self._config['recheck_interval']} seconds")
        time.sleep(self._config["recheck_interval"])

    def _process_webhook(self, webhook, value, bot_service, database):
        new_posts = self._get_new_posts(value, database)
        for post in new_posts:
            self._process_post(post, webhook, bot_service, database)

    def _get_new_posts(self, webhook_value, database):
        urls = self._get_urls_to_scrape(webhook_value)
        posts = []
        for url in urls:
            try:
                posts.extend(self._scraper.get_posts(url))
            except Exception as e:
                logger.error(f"Error while scraping {url}: {e}")

        return self._remove_dupes(posts, database)  # new or with a new price

    def _process_post(self, post, webhook, bot_service, database):
        try:
            json_item, json_user = self._scraper.get_post(post["url"])

            logger.debug(f"Item: {json_item}")
            logger.debug(f"User: {json_user}")

            self._on_data(json_item, database.items, database)
            self._on_data(json_user, database.users, database)

            bot_service.process_item(json_item, json_user, webhook)

            logger.debug(
                f"Sleeping for {self._config['request_interval']} seconds"
            )
            time.sleep(self._config["request_interval"])

        except Exception as e:
            logger.error(f"Error while scraping {post['url']}: {e}")
            bot_service.on_error(e)

    def _on_data(self, json_data, collection, database):
        return (
            self._on_exists(json_data, collection, database)
            if database.exists(json_data, collection)
            else self._on_not_exists(json_data, collection, database)
        )

    def _on_exists(self, json_data, collection, database):
        database.update(json_data, collection)
        return True

    def _on_not_exists(self, json_data, collection, database):
        database.insert(json_data, collection)
        return False

    def _get_urls_to_scrape(self, webhook_value):
        base_url = webhook_value["url"]
        page_limit = self._config["page_limit"]
        return [f"{base_url}&page={page}" for page in range(1, page_limit + 1)]

    def _remove_dupes(self, items, database):
        no_dupes = []

        all_items = list(database.items[1].find({}))
        pk = database.items[0]
        all_items_ids = [item[pk] for item in all_items]

        for item in items:
            item_id = int(item[pk])

            if item_id in all_items_ids:
                db_item = self._get_item_from_pk(pk, all_items, item_id)
                if not self._item_prices_are_same(item, db_item):
                    no_dupes.append(item)
            else:
                no_dupes.append(item)

        logger.info(f"Skipping {len(items) - len(no_dupes)} items already in database")
        return no_dupes

    def _get_item_from_pk(self, pk, items, item_id):
        return [item for item in items if item[pk] == item_id][0]

    def _item_prices_are_same(self, item, db_item):
        item_price = item["total_item_price"]["amount"]
        db_item_price = db_item["total_item_price"]
        if item_price != db_item_price:
            logger.info(f"Item {item['title']} has a new price: {item_price}€ instead of {db_item_price}€")
        return item_price == db_item_price
