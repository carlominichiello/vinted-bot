import json
import logging
import re

import requests
from bs4 import BeautifulSoup

from src.exceptions import AuthenticationError

logger = logging.getLogger("scraper")


class Scraper:
    def __init__(self, config):
        self._headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Cookie": config["cookie"],
        }

    def _get_soup(self, url):
        response = requests.get(url, headers=self._headers)
        return BeautifulSoup(response.content, "html.parser")

    def get_posts(self, url):
        logger.info(f"Scraping catalog: {url}")

        soup = self._get_soup(url)
        main_store_script = soup.find(
            "script",
            {"type": "application/json", "data-js-react-on-rails-store": "MainStore"},
        )
        main_store_json = json.loads(main_store_script.text)

        posts_by_id = main_store_json["items"]["catalogItems"]["byId"]
        for k, v in posts_by_id.items():
            v["id"] = k

        return list(posts_by_id.values())

    def get_post(self, url):
        logger.info(f"Scraping post: {url}")

        post_id = re.search(r"/items/(\d+)-", url).group(1)
        api_url = f"https://www.vinted.pl/api/v2/items/{post_id}"

        response = requests.get(api_url, headers=self._headers)
        json_response = response.json()

        if "item" not in json_response:
            logger.error(f"Error while scraping {url}: {json_response}")
            raise AuthenticationError("Please update your cookie in your config file")

        json_item = json_response["item"]

        json_user = json_item.pop("user")
        json_item["user"] = json_user["id"]
        return json_item, json_user
