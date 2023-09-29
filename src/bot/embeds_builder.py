import datetime as dt

import src.utils as utils


class EmbedBuilder:
    def __init__(self, config):
        self._config = config
        self._text_color = 16777215

    def build_embed(self, json_item, json_user):
        embed = self._build_base_embed(json_item)
        self._add_price_field(embed, json_item)
        self._add_size_field(embed, json_item)
        self.add_brand_field(embed, json_item)
        self._add_feedback_field(embed, json_user)
        self._add_location_field(embed, json_user)
        self._add_seller_field(embed, json_user)
        self._add_views_field(embed, json_item)
        self._add_favourites_field(embed, json_item)
        self._add_created_at_field(embed, json_item)
        return [embed]

    def _build_base_embed(self, json_item):
        embed = {
            "description": f"```\n{json_item['description']}```",
            "title": f"``👕`` **__{json_item['title']}__**",
            "color": self._text_color,
            "url": json_item["url"],
            "fields": [],
            "image": {"url": json_item["photos"][0]["url"]},
        }
        return embed

    def get_embed_value(self, json_data, key):
        if key in json_data:
            return f"{json_data[key]}"
        return "Unknown"

    def _add_price_field(self, embed, json_item):
        embed["fields"].append(
            {
                "name": "**``💶`` Price**",
                "value": f"**{self.get_embed_value(json_item, 'total_item_price')}€**",
                "inline": True,
            }
        )

    def _add_size_field(self, embed, json_item):
        embed["fields"].append(
            {
                "name": "**``📏`` Size**",
                "value": f"**{self.get_embed_value(json_item, 'size')}**",
                "inline": True,
            }
        )

    def add_brand_field(self, embed, json_item):
        embed["fields"].append(
            {
                "name": "**``🏷️`` Brand**",
                "value": f"**{self.get_embed_value(json_item, 'brand')}**",
                "inline": True,
            }
        )

    def _add_feedback_field(self, embed, json_user):
        positive_feedback_count = json_user["positive_feedback_count"]
        negative_feedback_count = json_user["negative_feedback_count"]
        neutral_feedback_count = json_user["neutral_feedback_count"]
        feedback_out_of_5 = utils.get_feedback_out_of_5(json_user)

        embed["fields"].append(
            {
                "name": "**``👍``/``👎`` Feedback**",
                "value": f"**{positive_feedback_count}/{negative_feedback_count} ({neutral_feedback_count} neutral) "
                         f"({feedback_out_of_5:.2f}/5)**",
                "inline": True,
            }
        )

    def _add_location_field(self, embed, json_user):
        city = self.get_embed_value(json_user, "city")
        country = self.get_embed_value(json_user, "country_title")

        embed["fields"].append(
            {
                "name": "**``📍`` Location**",
                "value": f"**{city}, {country}**",
                "inline": True,
            }
        )

    def _add_seller_field(self, embed, json_user):
        embed["fields"].append(
            {
                "name": "**``👤`` Seller**",
                "value": f"**{self.get_embed_value(json_user, 'login')}**",
                "inline": True,
            }
        )

    def _add_views_field(self, embed, json_item):
        embed["fields"].append(
            {
                "name": "**``👀`` Views**",
                "value": f"**{self.get_embed_value(json_item, 'view_count')}**",
                "inline": True,
            }
        )

    def _add_favourites_field(self, embed, json_item):
        embed["fields"].append(
            {
                "name": "**``❤️`` Favourites**",
                "value": f"**{self.get_embed_value(json_item, 'favourite_count')}**",
                "inline": True,
            }
        )

    def _add_created_at_field(self, embed, json_item):
        created_at = dt.datetime.fromisoformat(json_item["created_at_ts"]).strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        embed["fields"].append(
            {
                "name": "**``📅`` Created at**",
                "value": f"**{created_at}**",
                "inline": True,
            }
        )
