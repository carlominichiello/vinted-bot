import json
import logging
import re
import threading
import time
from src.scraping.cookies_manager import CookiesManager

import requests
from bs4 import BeautifulSoup

from src.exceptions import AuthenticationError

logger = logging.getLogger("scraper")


class Scraper:
    def __init__(self):
        self._headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
            "Connection": "keep-alive",
        }
        self._cookies_manager = CookiesManager(self._headers)
        self._random_scraping = False

    def scrape_items(self,
                     start_page=1,
                     end_page=1,
                     catalog_ids=None,
                     color_ids=None,
                     brand_ids=None,
                     size_ids=None,
                     material_ids=None,
                     video_game_rating_ids=None,
                     status_ids=None,
                     currency="EUR",
                     price_from=None,
                     price_to=None,
                     order="relevance",
                        ):
        logger.info(f"Scraping posts from query")

        base_url = "https://www.vinted.fr/api/v2/catalog/items"
        query_params = {
            "page": start_page,
            "catalog_ids": catalog_ids,
            "color_ids": color_ids,
            "brand_ids": brand_ids,
            "size_ids": size_ids,
            "material_ids": material_ids,
            "video_game_rating_ids": video_game_rating_ids,
            "status_ids": status_ids,
            "currency": currency,
            "price_from": price_from,
            "price_to": price_to,
            "order": order,
        }

        items_ids = []

        scrape_all = False
        if end_page == -1:
            scrape_all = True

        while query_params['page'] <= end_page or scrape_all:
            response = requests.get(base_url, params=query_params, headers=self._headers)
            json_response = response.json()

            current_page = json_response["pagination"]["current_page"]
            total_pages = json_response["pagination"]["total_pages"]

            items = json_response["items"]
            items_ids.extend([item["id"] for item in items])

            if current_page == total_pages:
                break

            query_params["page"] = current_page + 1
        return items_ids

    def scrape_item(self, item_id):
        logger.info(f"Scraping item: {item_id}")

        api_url = f"https://www.vinted.fr/api/v2/items/{item_id}"

        response = requests.get(api_url, headers=self._headers)
        json_response = response.json()

        json_item = json_response["item"]

        json_user = json_item.pop("user")
        json_item["user"] = json_user["id"]
        return json_item, json_user

    def scrape_user(self, user_id):
        logger.info(f"Scraping user: {user_id}")

        api_url = f"https://www.vinted.fr/api/v2/users/{user_id}"

        response = requests.get(api_url, headers=self._headers)
        json_response = response.json()

        json_user = json_response["user"]
        return json_user

    def start_random_scrape_thread(self):
        self._random_scrape_thread = threading.Thread(
            target=self._random_scrape, daemon=True
        )
        self._random_scrape_thread.start()
        self._random_scraping = True

    def stop_random_scrape_thread(self):
        self._random_scraping = False

    def _random_scrape(self):
        print("Random scrape started")
        while self._random_scraping:
            print("Random scrape")
            time.sleep(1)
