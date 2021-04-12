import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from ._threading import map_threads


def write_email(user, posts):
    """Main function to construct email sender, recipients, and content for
    new craigslist housing posts."""
    # Add new posts to Email object in text and markup format
    current_mail = add_new_posts(Email(), posts)

    # Add Email metadata
    metadata = EmailMetadata()
    metadata.sender_email = os.environ.get("EMAIL_USER")
    metadata.sender_password = os.environ.get("EMAIL_PASS")
    metadata.receiver_email = user["email"]
    metadata.subject = f"New housing near {user['zip_code']}"
    metadata.construct_MIME()

    # Build header email content
    email_content = f"Hey {user['name'].title()}, I found some new housing deals on Craigslist near {user['zip_code']}. To stop these emails, write 'STOP' to ira89@icloud.com."
    try:
        # Attempt to send email to user if new posts found
        text, html = current_mail.markup(email_content)
        if text:  # Make sure no empty str returned
            send_email(metadata, text, html)
    except AttributeError:
        # Markup returned None
        pass


class EmailMetadata:
    """Constructor for email metadata."""

    def __init__(self):
        self.sender_email = ""
        self.sender_password = ""
        self.receiver_email = ""
        self.subject = ""
        self.message = ""

    def construct_MIME(self):
        """Construct MIMEMultipart object from instance attributes."""
        self.message = MIMEMultipart("alternative")
        self.message["Subject"] = self.subject
        self.message["From"] = self.sender_email
        self.message["To"] = ""


class Email:
    """Construct email body from new posts."""

    def __init__(self):
        self.text_body = ""
        self.html_body = ""

    def body(self, content, html_content):
        """Append post information to string template (text and html)."""
        self.text_body += content
        self.html_body += html_content

    def markup(self, message):
        """Concatenate self.text_body and self.html_body in markup format for email."""
        text_markup = f"""\
            {self.text_body}
        """
        html_markup = f"""\
            <html>
            <body>
                <p>
                {message}
                </p>
                <br>
                <p>
                {self.html_body}
                </p>
            </body>
            </html>
        """

        return text_markup, html_markup


def add_new_posts(current_mail, posts_df):
    """Add post attributes to email object if post has valid content."""
    if posts_df.shape[0] == 0:
        return None

    posts = [post for _, post in posts_df.iterrows()]
    # Thread parsing of verifying posts
    # Is threading the right approach here?
    response = map_threads(parse_verify_posts, posts)

    for post in response:
        # If post was invalid
        if post is None:
            continue

        content = f"""
        ${post["price"]} / mo - {post["bedrooms"]} BR - {post["location"].title()}
        * Title: {post["title"]}
        * Housing type: {post["housing_type"]}
        * Address: {post["address"]}
        * Parking: {post["parking"]}
        * Laundry: {post["laundry"]}
        """
        html_content = f"""
        ${post["price"]} / mo - {post["bedrooms"]} BR - {post["location"].title()} <br>
        <b><a href="{post["url"]}">{post["title"]}</a></b>
        <ul>
            <li>Housing type: {post["housing_type"]}</li>
            <li>Address: {post["address"]}</li>
            <li>Parking: {post["parking"]}</li>
            <li>Laundry: {post["laundry"]}</li>
        </ul>
        <hr>"""

        current_mail.body(content, html_content)

    return current_mail


def parse_verify_posts(post):
    """Parse posts to retrieve attributes and verify a valid url -- return None
    if invalid. This function works with the map_threads module from _threadings.py"""
    post_content = {"url": post["URL"]}

    # If any post has bad content, return None to caller
    invalid_flag = "This posting has been flagged for removal."
    deleted_flag = "This posting has been deleted by its author."
    content = requests.get(post_content["url"]).content.decode("utf-8")
    if any(bad_flag in content for bad_flag in [invalid_flag, deleted_flag]):
        return None

    # Add to post_content dictionary in standardized format
    post_content["title"] = post["Title"]
    post_content["location"] = post["Neighborhood"]
    post_content["price"] = "%.0f" % post["Price"]
    post_content["bedrooms"] = post["Bedrooms"]
    post_content["address"] = post["Address"]
    post_content["housing_type"] = post["HousingType"]
    post_content["parking"] = post["Parking"]
    post_content["laundry"] = post["Laundry"]

    return post_content


def send_email(metadata, text, html):
    """Build and send email from Gmail account."""
    text_mail = MIMEText(text, "plain")
    html_mail = MIMEText(html, "html")
    message = metadata.message

    # Attach both text and html versions of email
    message.attach(text_mail)
    message.attach(html_mail)

    ssl_context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl_context) as server:
        server.login(metadata.sender_email, metadata.sender_password)
        if isinstance(metadata.receiver_email, list):
            # Send email to multiple users if user email attribute is a list
            for recipient in metadata.receiver_email:
                message["To"] = recipient
                server.sendmail(metadata.sender_email, recipient, message.as_string())
        else:
            # Single user email
            message["To"] = metadata.receiver_email
            server.sendmail(metadata.sender_email, metadata.receiver_email, message.as_string())
