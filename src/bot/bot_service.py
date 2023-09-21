import logging

import requests
import datetime as dt

from src.bot.embeds_builder import EmbedsBuilder

logger = logging.getLogger("bot")


class BotService:
    def __init__(self, bot_config, database_config, scraper_config):
        self.bot_config = bot_config
        self.database_config = database_config
        self.scraper_config = scraper_config

        self.embeds_builder = EmbedsBuilder(bot_config)

    def get_webhooks(self):
        return self.bot_config["watch"]

    def process_item(self, json_data, webhook):
        if self.validate_item(json_data, webhook):
            self.send_item(json_data, webhook)

    def validate_item(self, json_data, webhook):
        if "min_rating" in self.bot_config["watch"][webhook]:
            if json_data["user"]["feedback_out_of_5"] < float(
                self.bot_config["watch"][webhook]["min_rating"]
            ):
                logger.info(
                    f"Rejected item: {json_data['title']} - User rating too low ({json_data['user']['feedback_out_of_5']} < {self.bot_config['watch'][webhook]['min_rating']})"
                )
                return False
        if "min_favourites" in self.bot_config["watch"][webhook]:
            if json_data["favourite_count"] < int(
                self.bot_config["watch"][webhook]["min_favourites"]
            ):
                logger.info(
                    f"Rejected item: {json_data['title']} - Favourites too low ({json_data['favourite_count']} < {self.bot_config['watch'][webhook]['min_favourites']})"
                )
                return False
        if "max_days_offset" in self.bot_config["watch"][webhook]:
            created_at = dt.datetime.fromisoformat(json_data["created_at"])
            created_at = dt.datetime(
                created_at.year, created_at.month, created_at.day, hour=created_at.hour, minute=created_at.minute, second=created_at.second
            )
            if (dt.datetime.now() - created_at).days > int(
                self.bot_config["watch"][webhook]["max_days_offset"]
            ):
                logger.info(
                    f"Rejected item: {json_data['title']} - Created too long ago ({(dt.datetime.now() - created_at).days} > {self.bot_config['watch'][webhook]['max_days_offset']})"
                )
                return False
        return True

    def send_item(self, json_data, webhook):
        logger.debug(f"Sending item to Discord: wh {webhook} - {json_data}")
        json_data = self.format_item(json_data)
        self.send_data(json_data, webhook)

    def format_item(self, json_data):
        embeds = self.embeds_builder.build_embeds(json_data)
        return {
            "username": "Vinted",
            "avatar_url": "https://asset.brandfetch.io/idQxXNbl4Z/idqVdsLYmE.jpeg",
            "embeds": embeds,
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "Voir l'annonce",
                            "style": 5,
                            "url": json_data["url"],
                        }
                    ],
                }
            ],
        }

    def on_start(self, webhooks):
        n_webhooks = len(webhooks)
        data = {
            "username": "Vinted",
            "avatar_url": "https://asset.brandfetch.io/idQxXNbl4Z/idqVdsLYmE.jpeg",
            "content": f"️️️🔍 Started searching for items.\n"
                       f"{n_webhooks} watch{'es' if n_webhooks > 1 else ''} active.",
        }
        logs_channel = self.bot_config["logs_channel"]
        if logs_channel:
            self.send_data(data, logs_channel)

    def on_finish(self):
        data = {
            "username": "Vinted",
            "avatar_url": "https://asset.brandfetch.io/idQxXNbl4Z/idqVdsLYmE.jpeg",
            "content": f"️️🏁 Finished searching for items. Next recheck in {self.scraper_config['recheck_interval'] / 60} minutes.",
        }
        logs_channel = self.bot_config["logs_channel"]
        if logs_channel:
            self.send_data(data, logs_channel)

    def send_data(self, data, webhook):
        res = requests.post(webhook, json=data)
        if res:
            if res.status_code == 204:
                logger.info(f"Sent message to Discord: {res.status_code} {res.text}")
            else:
                logger.error(
                    f"Couldn't send message to Discord: {res.status_code} {res.text}"
                )
