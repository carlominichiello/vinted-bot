import datetime as dt
import logging

import requests

import src.utils as utils
from src.bot.embeds_builder import EmbedBuilder

logger = logging.getLogger("bot")


class BotService:
    def __init__(self, bot_config, database_config, scraper_config):
        self.bot_config = bot_config
        self.database_config = database_config
        self.scraper_config = scraper_config

        self.embeds_builder = EmbedBuilder(bot_config)

    def get_webhooks(self):
        return self.bot_config["watch"]

    def process_item(self, json_item, json_user, webhook):
        if self.validate_item(json_item, json_user, webhook):
            self.send_item(json_item, json_user, webhook)

    def validate_item(self, json_item, json_user, webhook):
        return (
            self._validate_min_rating(json_item, json_user, webhook)
            and self._validate_min_favourites(json_item, webhook)
            and self._validate_max_days_offset(json_item, webhook)
        )

    def _validate_min_rating(self, json_item, json_user, webhook):
        if "min_rating" in self.bot_config["watch"][webhook]:
            user_rating = utils.get_feedback_out_of_5(json_user)
            if user_rating < float(self.bot_config["watch"][webhook]["min_rating"]):
                logger.info(
                    f"Rejected item: {json_item['title']} - User rating too low ({user_rating} < {self.bot_config['watch'][webhook]['min_rating']})"
                )
                return False
        return True

    def _validate_min_favourites(self, json_item, webhook):
        if "min_favourites" in self.bot_config["watch"][webhook] and json_item[
            "favourite_count"
        ] < int(self.bot_config["watch"][webhook]["min_favourites"]):
            logger.info(
                f"Rejected item: {json_item['title']} - Favourites too low ({json_item['favourite_count']} < {self.bot_config['watch'][webhook]['min_favourites']})"
            )
            return False
        return True

    def _validate_max_days_offset(self, json_item, webhook):
        if "max_days_offset" in self.bot_config["watch"][webhook]:
            created_at = dt.datetime.fromisoformat(json_item["created_at_ts"])
            created_at = dt.datetime(
                created_at.year,
                created_at.month,
                created_at.day,
                hour=created_at.hour,
                minute=created_at.minute,
                second=created_at.second,
            )
            if (dt.datetime.now() - created_at).days > int(
                self.bot_config["watch"][webhook]["max_days_offset"]
            ):
                logger.info(
                    f"Rejected item: {json_item['title']} - Created too long ago ({(dt.datetime.now() - created_at).days} > {self.bot_config['watch'][webhook]['max_days_offset']})"
                )
                return False
        return True

    def send_item(self, json_item, json_user, webhook):
        logger.debug(f"Sending item to Discord: wh {webhook} - {json_item}")
        json_data = self._format_item(json_item, json_user)
        self.send_data(json_data, webhook)

    def _format_item(self, json_item, json_user):
        embeds = self.embeds_builder.build_embed(json_item, json_user)
        return {
            "embeds": embeds,
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "View on Vinted",
                            "style": 5,
                            "url": json_item["url"],
                        }
                    ],
                }
            ],
        }

    def on_start(self, webhooks):
        n_webhooks = len(webhooks)
        data = {
            "content": f"️️️🔍 Started searching for items.\n"
            f"{n_webhooks} watch{'es' if n_webhooks > 1 else ''} active.",
        }
        logs_channel = self.bot_config["logs_channel"]
        if logs_channel:
            self.send_data(data, logs_channel)

    def on_finish(self):
        data = {
            "content": f"️️🏁 Finished searching for items. Next recheck in {self.scraper_config['recheck_interval'] / 60} minutes.",
        }
        logs_channel = self.bot_config["logs_channel"]
        if logs_channel:
            self.send_data(data, logs_channel)

    def on_error(self, error):
        data = {
            "content": f"️️❌ Error occured while searching for items: {error}",
        }
        logs_channel = self.bot_config["logs_channel"]
        if logs_channel:
            self.send_data(data, logs_channel)

    def send_data(self, data, webhook):
        res = requests.post(webhook, json=self._format_data(data))
        if res:
            if res.status_code == 204:
                logger.info(f"Sent message to Discord: {res.status_code} {res.text}")
            else:
                logger.error(
                    f"Couldn't send message to Discord: {res.status_code} {res.text}"
                )

    def _format_data(self, data):
        common_data = {
            "username": "Vinted",
            "avatar_url": "https://asset.brandfetch.io/idQxXNbl4Z/idqVdsLYmE.jpeg",
        }
        return {**common_data, **data}
