import logging
import time
import threading

from src.scraping.scraper import Scraper
from src.scraping.query_generator import QueryGenerator

logger = logging.getLogger("scraper")


class Monitor:
    def __init__(self, config):
        self._config = config
        self._scraper = Scraper(config)
        self._query_generator = QueryGenerator()
        self._random_scraping = False

    def run(self, bot_service, database):
        webhooks = bot_service.get_webhooks()
        logger.info(f"Monitoring {len(webhooks)} urls")
        bot_service.on_start(webhooks)

        for webhook, value in webhooks.items():
            self._process_webhook(webhook, value, bot_service, database)

        bot_service.on_finish()
        logger.info(f"Next recheck in {self._config['recheck_interval']} seconds")
        self._wait(bot_service, database)

    def _wait(self, bot_service, database):
        webhook, value = bot_service.get_random_scraping_webhook()
        self._start_random_scrape_thread(webhook, value, bot_service, database) if webhook else None

        time_start = time.time()
        while True:
            time.sleep(1)
            if time.time() - time_start > self._config["recheck_interval"]:
                break
        self._stop_random_scrape_thread() if webhook else None

    def _process_webhook(self, webhook, value, bot_service, database, page_start=1, page_end=1):
        params = self._query_generator.get_query(value["url"])
        items_ids = self._scraper.scrape_items(**params)
        new_items_ids = self._remove_dupes(items_ids, database)
        logger.info(f"Found {len(new_items_ids)} new items for {value['url']}")
        for item_id in new_items_ids:
            self._process_item(item_id, webhook, bot_service, database)

    def _process_item(self, item_id, webhook, bot_service, database):
        try:
            json_item, json_user = self._scraper.scrape_item(item_id)

            logger.debug(f"Item: {json_item}")
            logger.debug(f"User: {json_user}")

            self._on_data(json_item, database.items, database)
            self._on_data(json_user, database.users, database)

            bot_service.process_item(json_item, json_user, webhook)

            logger.debug(f"Sleeping for {self._config['request_interval']} seconds")
            time.sleep(self._config["request_interval"])

        except Exception as e:
            logger.error(f"Error while scraping {item_id}: {e}")
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

    def _remove_dupes(self, items_ids, database):
        db_items = list(database.items[1].find({}))
        db_items_ids = [item['id'] for item in db_items]
        return [item_id for item_id in items_ids if item_id not in db_items_ids]

    def _start_random_scrape_thread(self, webhook, value, bot_service, database):
        self._random_scraping = True
        self._random_scrape_thread = threading.Thread(target=self._random_scrape, args=(webhook, value, bot_service, database))
        self._random_scrape_thread.start()

    def _stop_random_scrape_thread(self):
        self._random_scraping = False

    def _random_scrape(self, webhook, value, bot_service, database):
        logger.info(f"Starting random scraping for {value['url']}")
        page_start = 1
        while self._random_scraping:
            self._process_webhook(webhook, value, bot_service, database, page_start)
            page_start += 1
