import datetime as dt
from dataclasses import dataclass


@dataclass
class User:
    vinted_id: str
    username: str
    is_pro: bool
    profile_url: str
    positive_feedback_count: int
    negative_feedback_count: int
    neutral_feedback_count: int
    feedback_out_of_5: float
    item_count: int
    given_item_count: int
    taken_item_count: int
    followers_count: int
    following_count: int
    city: str
    country: str
    about: str


@dataclass
class Item:
    vinted_id: str
    title: str
    description: str
    price: float
    brand: str
    url: str
    boosted: bool
    photo: str
    favourite_count: int
    size: str
    created_at: dt.datetime
    user: User
