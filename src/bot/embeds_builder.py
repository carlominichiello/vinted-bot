import datetime as dt


class EmbedsBuilder:
    def __init__(self, config):
        self.config = config
        self.text_color = 16777215

    def build_embeds(self, json_data):
        embed = self.build_base_embed(json_data)
        self.add_price_field(embed, json_data)
        self.add_size_field(embed, json_data)
        self.add_brand_field(embed, json_data)
        self.add_feedback_field(embed, json_data)
        self.add_location_field(embed, json_data)
        self.add_seller_field(embed, json_data)
        self.add_favourites_field(embed, json_data)
        self.add_created_at_field(embed, json_data)
        return [embed]

    def build_base_embed(self, json_data):
        embed = {
            "description": f"```\n{json_data['description']}```",
            "title": f"``👕`` **__{json_data['title']}__**",
            "color": self.text_color,
            "url": json_data["url"],
            "fields": [],
            "image": {"url": json_data["photo"]},
        }
        return embed

    def get_embed_value(self, json_data, key):
        if key in json_data:
            return f"{json_data[key]}"
        return "Unknown"

    def add_price_field(self, embed, json_data):
        embed["fields"].append(
            {
                "name": "**``💶`` Price**",
                "value": f"**{self.get_embed_value(json_data, 'price')}€**",
                "inline": True,
            }
        )

    def add_size_field(self, embed, json_data):
        embed["fields"].append(
            {
                "name": "**``📏`` Size**",
                "value": f"**{self.get_embed_value(json_data, 'size')}**",
                "inline": True,
            }
        )

    def add_brand_field(self, embed, json_data):
        embed["fields"].append(
            {
                "name": "**``🏷️`` Brand**",
                "value": f"**{self.get_embed_value(json_data, 'brand')}**",
                "inline": True,
            }
        )

    def add_feedback_field(self, embed, json_data):
        positive_feedback = 0
        negative_feedback = 0
        feedback_out_of_5 = 0
        if "user" in json_data:
            if "positive_feedback_count" in json_data["user"]:
                positive_feedback = int(json_data["user"]["positive_feedback_count"])
            if "negative_feedback_count" in json_data["user"]:
                negative_feedback = int(json_data["user"]["negative_feedback_count"])
            if "feedback_out_of_5" in json_data["user"]:
                feedback_out_of_5 = float(json_data["user"]["feedback_out_of_5"])

        embed["fields"].append(
            {
                "name": "**``👍``/``👎`` Feedback**",
                "value": f"**{positive_feedback}/{negative_feedback} ({feedback_out_of_5:.2f}/5)**",
                "inline": True,
            }
        )

    def add_location_field(self, embed, json_data):
        city = "Unknown"
        country = "Unknown"
        if "user" in json_data:
            if "city" in json_data["user"]:
                city = json_data["user"]["city"]
            if "country" in json_data["user"]:
                country = json_data["user"]["country"]

        embed["fields"].append(
            {
                "name": "**``📍`` Location**",
                "value": f"**{city}, {country}**",
                "inline": True,
            }
        )

    def add_seller_field(self, embed, json_data):
        username = "Unknown"
        if "user" in json_data:
            if "username" in json_data["user"]:
                username = json_data["user"]["username"]

        embed["fields"].append(
            {"name": "**``👤`` Seller**", "value": f"**{username}**", "inline": True}
        )

    def add_favourites_field(self, embed, json_data):
        favourites = "Unknown"
        if "favourite_count" in json_data:
            favourites = json_data["favourite_count"]

        embed["fields"].append(
            {
                "name": "**``❤️`` Favourites**",
                "value": f"**{favourites}**",
                "inline": True,
            }
        )

    def add_created_at_field(self, embed, json_data):
        created_at = "Unknown"
        if "created_at" in json_data:
            created_at = dt.datetime.fromisoformat(json_data["created_at"]).strftime(
                "%d/%m/%Y %H:%M:%S"
            )

        embed["fields"].append(
            {
                "name": "**``📅`` Created at**",
                "value": f"**{created_at}**",
                "inline": True,
            }
        )
