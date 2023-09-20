import json
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("scraper")


class Scraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }

    def get_soup(self, url):
        response = requests.get(url, headers=self.headers)
        return BeautifulSoup(response.content, "html.parser")

    def get_posts(self, url):
        logger.info(f"Scraping catalog: {url}")

        soup = self.get_soup(url)
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

        soup = self.get_soup(url)

        post_details = self.get_post_details(soup)["item"]
        user_details = self.get_user_details(soup)["user"]

        return post_details, user_details

    def get_post_details(self, post_soup):
        script = post_soup.find("script", {"data-component-name": "ItemDetails"})
        return json.loads(script.text)

    def get_user_details(self, post_soup):
        script = post_soup.find("script", {"data-component-name": "ItemUserInfo"})
        return json.loads(script.text)
