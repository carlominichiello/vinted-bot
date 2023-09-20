import datetime as dt

from src.datamodels.models import Item, User


def get_item_from_scraping(catalog_data, item_details, user_data):
    return Item(
        vinted_id=catalog_data["id"],
        title=item_details["title"],
        description=item_details["description"],
        price=catalog_data["total_item_price"]["amount"],
        brand=catalog_data["brand_title"],
        url=catalog_data["url"],
        boosted=catalog_data["promoted"],
        photo=catalog_data["photo"]["url"],
        favourite_count=catalog_data["favourite_count"],
        size=catalog_data["size_title"],
        created_at=dt.datetime.strptime(
            item_details["created_at_ts"], "%Y-%m-%dT%H:%M:%S%z"
        ),
        user=get_user_from_scraping(user_data),
    )


def get_user_from_scraping(user_data):
    return User(
        vinted_id=user_data["id"],
        username=user_data["login"],
        is_pro=user_data["business"],
        profile_url=f"https://www.vinted.fr{user_data['path']}",
        positive_feedback_count=user_data["positive_feedback_count"],
        negative_feedback_count=user_data["negative_feedback_count"],
        neutral_feedback_count=user_data["neutral_feedback_count"],
        feedback_out_of_5=feedback_out_of_5(user_data),
        item_count=user_data["item_count"],
        given_item_count=user_data["given_item_count"],
        taken_item_count=user_data["taken_item_count"],
        followers_count=user_data["followers_count"],
        following_count=user_data["following_count"],
        city=user_data["city"],
        country=user_data["country_title"],
        about=user_data["about"],
    )


def feedback_out_of_5(user_data):
    positive_feedback_count = int(user_data["positive_feedback_count"])
    negative_feedback_count = int(user_data["negative_feedback_count"])
    if positive_feedback_count + negative_feedback_count > 0:
        return round(
            positive_feedback_count
            / (positive_feedback_count + negative_feedback_count)
            * 5,
            2,
        )
    else:
        return 0


def item_to_json(item):
    return {
        "vinted_id": item.vinted_id,
        "title": item.title,
        "description": item.description,
        "price": item.price,
        "brand": item.brand,
        "url": item.url,
        "boosted": item.boosted,
        "photo": item.photo,
        "favourite_count": item.favourite_count,
        "size": item.size,
        "created_at": item.created_at.isoformat(),
        "user": user_to_json(item.user),
    }


def user_to_json(user):
    return {
        "vinted_id": user.vinted_id,
        "username": user.username,
        "is_pro": user.is_pro,
        "profile_url": user.profile_url,
        "positive_feedback_count": user.positive_feedback_count,
        "negative_feedback_count": user.negative_feedback_count,
        "neutral_feedback_count": user.neutral_feedback_count,
        "feedback_out_of_5": user.feedback_out_of_5,
        "item_count": user.item_count,
        "given_item_count": user.given_item_count,
        "taken_item_count": user.taken_item_count,
        "followers_count": user.followers_count,
        "following_count": user.following_count,
        "city": user.city,
        "country": user.country,
        "about": user.about,
    }


def json_items_eq(item1, item2):
    return (
        item1["vinted_id"] == item2["vinted_id"]
        and item1["price"] == item2["price"]
        and item1
    )
