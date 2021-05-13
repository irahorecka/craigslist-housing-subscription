import pandas as pd
import pycraigslist
from pycraigslist.exceptions import MaximumRequestsError

# Create a unique enough key to allow segregating of scraped craigslist content
CODE_BREAK = ";n@nih;"


def get_apa_posts(user_filter):
    """Applies user's filters to apa query and returns pandas data frame of posts within filter.
    Filter must have key 'filters' and 'site'. 'area' is optional"""
    filters = user_filter["filters"]
    # Add zip and search distance from user info to query filter
    filters["zip_code"] = user_filter["zip_code"]
    filters["search_distance"] = user_filter["search_distance"]
    # Build pycraigslist.housing.apa object for search
    try:
        user_search = pycraigslist.housing.apa(
            site=user_filter["site"], area=user_filter.get("area", ""), filters=filters
        )
        return get_posts_df(user_search)
    except MaximumRequestsError:
        return get_apa_posts(user_filter)


def get_posts_df(user_search):
    """Searches, parses, and returns post to caller as a pandas DataFrame."""
    # Gets header for posts, almost a metadata to explain subsequent content
    posts = get_header()
    for post in user_search.search_detail(limit=1000):
        posts.append(parse_post(post))
    posts = [post.split(CODE_BREAK) for post in posts]
    posts_column = posts.pop(0)

    return pd.DataFrame(posts, columns=posts_column)


def get_header():
    """Returns header string to caller."""
    return [
        f"PostID{CODE_BREAK}RepostID{CODE_BREAK}Title{CODE_BREAK}URL{CODE_BREAK}"
        f"DateUpdated{CODE_BREAK}TimeUpdated{CODE_BREAK}Price{CODE_BREAK}"
        f"Neighborhood{CODE_BREAK}Address{CODE_BREAK}HousingType{CODE_BREAK}"
        f"Laundry{CODE_BREAK}Parking{CODE_BREAK}Bedrooms{CODE_BREAK}AreaFt2"
    ]


def parse_post(post_json):
    """Returns post content string to caller."""
    return "".join(
        [
            f"{post_json['id']}{CODE_BREAK}{post_json['repost_of']}{CODE_BREAK}{post_json['title']}{CODE_BREAK}{post_json['url']}{CODE_BREAK}",
            f"{post_json['last_updated'][0:10]}{CODE_BREAK}{post_json['last_updated'][11:]}{CODE_BREAK}",
            f"{post_json['price']}{CODE_BREAK}{post_json['neighborhood']}{CODE_BREAK}",
            f'{post_json["address"]}{CODE_BREAK}{post_json["housing_type"]}{CODE_BREAK}',
            f'{post_json["laundry"]}{CODE_BREAK}{post_json["parking"]}{CODE_BREAK}',
            f"{post_json['bedrooms']}{CODE_BREAK}{post_json.get('area-ft2', 0)}",
        ]
    )
