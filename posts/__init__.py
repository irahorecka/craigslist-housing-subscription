from .craigslist import get_apa_posts
from .parse import parse_content
from .db import return_new, drop_db


def get(users):
    for user in users:
        users_posts = get_apa_posts(user)
        parsed_posts = parse_content(users_posts)
        yield return_new(parsed_posts)


def drop_contents():
    drop_db()
