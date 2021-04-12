"""
Main file to find and send user Craigslist housing posts.
"""

import time
import users
import posts
import mail


def main():
    """Main app to execute subscription based email notifications."""
    users_json = users.get_users()
    # At start of subscription, drop all content and populate db without sending email
    posts.drop_contents()
    for _ in posts.get(users_json):
        pass

    while True:
        # Sleep for a day (-80 seconds) to fetch posts
        print("sleeping...")
        time.sleep(86320)
        user_posts = zip(users_json, posts.get(users_json))
        for user, post in user_posts:
            mail.write_email(user, post)


if __name__ == "__main__":
    main()
