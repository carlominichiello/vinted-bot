import logging
import time
import threading
import random

import requests.exceptions
import src.exceptions

from src.scraping.scraper import Scraper
from src.scraping.query_generator import QueryGenerator

logger = logging.getLogger("scraper")


class Monitor:
    def __init__(self, config):
        self._config = config
        self._scraper = Scraper(config)
        self._query_generator = QueryGenerator()
        self._threads = []

    def run_watch(self, bot_service, database):
        watch_webhooks = bot_service.get_webhooks()
        logger.info(f"Monitoring {len(watch_webhooks)} urls")
        bot_service.on_start(watch_webhooks)

        for webhook, value in watch_webhooks.items():
            try:
                self._process_url(value['url'], database, webhook=webhook, bot_service=bot_service)
            except requests.exceptions.HTTPError as e:
                logger.error(f"Error while scraping {value['url']}: {e}")
                bot_service.on_error(e)

        bot_service.on_finish()
        logger.info(f"Next recheck in {self._config['recheck_interval']} seconds")
        self._wait()

    def run_background_scraping(self, bot_service, database):
        background_scraping_webhooks = bot_service.get_background_scraping_webhooks()
        for webhook, value in background_scraping_webhooks.items():
            thread_id = random.randint(0, 100000)
            self._start_background_scrape_thread(value['url'], database, thread_id, webhook, bot_service)

    def run_random_scraping(self, bot_service, database):
        self._start_random_scrape_thread(bot_service, database)

    def _wait(self):
        time_start = time.time()
        while True:
            time.sleep(1)
            if time.time() - time_start > self._config["recheck_interval"]:
                break

    def _process_url(self, url, database, page_start=1, page_end=None, webhook=None, bot_service=None):
        params = self._query_generator.get_query(url)

        items_ids = self._scraper.scrape_items(**params, start_page=page_start, end_page=page_end)
        if not items_ids:
            raise requests.exceptions.HTTPError(f"Items not found for {url}")

        new_items_ids = database.get_no_dupes(database.items, items_ids)
        logger.info(f"Found {len(new_items_ids)} new items for {url} (page start: {page_start}, page end: {page_end})")
        for item_id in new_items_ids:
            self._process_item(item_id, database, webhook, bot_service)

    def _process_item(self, item_id, database, webhook=None, bot_service=None):
        try:
            json_item, json_user = self._scraper.scrape_item(item_id)

            logger.debug(f"Item: {json_item}")
            logger.debug(f"User: {json_user}")

            self._on_data(json_item, database.items, database)
            self._on_data(json_user, database.users, database)

            if webhook and bot_service:
                bot_service.process_item(json_item, json_user, webhook)

            logger.debug(f"Sleeping for {self._config['request_interval']} seconds")
            time.sleep(self._config["request_interval"])

        except src.exceptions.RetryException as e:
            logger.error(f"Error while scraping {item_id}, retrying: {e}")

            if bot_service:
                bot_service.on_error(e)

            self._process_item(item_id, database, webhook, bot_service)

        except requests.exceptions.HTTPError as e:
            logger.error(f"Error while scraping {item_id}: {e}")

            if bot_service:
                bot_service.on_error(e)
        
        except Exception as e:
            logger.error(f"Error while scraping {item_id}: {e}")

            if bot_service:
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

    def _start_background_scrape_thread(self, url, database, thread_id, webhook=None, bot_service=None):
        self._threads.append(thread_id)
        self._background_scrape_thread = threading.Thread(target=self._background_scrape, args=(url, database, thread_id, webhook, bot_service))
        self._background_scrape_thread.start()

    def _stop_background_scrape_thread(self, thread_id):
        self._threads.remove(thread_id)

    def _background_scrape(self, url, database, thread_id, webhook=None, bot_service=None):
        logger.info(f"Starting background scraping for {url}")
        logger.debug(f"Thread id: {thread_id}")
        page_start = 100
        while thread_id in self._threads:
            try:
                self._process_url(url, database, page_start, webhook=webhook, bot_service=bot_service)
            except requests.exceptions.HTTPError as e:
                logger.error(f"Error while scraping {url}: {e}")

                if bot_service and webhook:
                    data = {
                        'content': "️️❌ No more items found",
                    }
                    bot_service.send_data(data, webhook)

                self._stop_background_scrape_thread(thread_id)
            page_start += 1

    def _start_random_scrape_thread(self, bot_service, database):
        self._random_scrape_thread = threading.Thread(target=self._random_scrape, args=(bot_service, database))
        self._random_scrape_thread.start()

    def _random_scrape(self, bot_service, database):
        logger.info(f"Starting random scraping")
        while True:
            while not self._threads:
                try:
                    url = self._get_random_scrape_url()
                    page_start = 1
                    while True:
                        self._process_url(url, database, page_start=page_start, bot_service=bot_service)
                        page_start += 1

                except requests.exceptions.HTTPError as e:
                    logger.error(f"Error while scraping {url}: {e}")

                    if bot_service:
                        bot_service.on_error(e)
            self._wait()

    def _get_random_scrape_url(self):
        cats = self._scraper.scrape_cats()
        cats_list = list(cats.keys())
        random_cat = random.choice(cats_list)
        url = f"https://www.vinted.fr/catalog?catalog[]={random_cat}"
        return url
