import os
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

Base = declarative_base()


class Post(Base):
    """Database table to store Craigslist Housing information post filter
    and clean."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, unique=True)
    title = Column(String)
    url = Column(String, unique=True)
    date = Column(DateTime)
    price = Column(Float)
    neighborhood = Column(String)
    address = Column(String)
    housing_type = Column(String)
    laundry = Column(String)
    parking = Column(String)
    bedrooms = Column(Integer)
    sqft = Column(Integer)


def return_new(posts):
    """Return pandas dataframe with new posts after comparison with
    user's data in database. Send new posts to write to user's database."""
    engine = get_engine()
    session = get_session(engine)
    # Declare empty pandas DataFrame to store new posts
    new_posts = pd.DataFrame(columns=list(posts))
    for _, post in posts.iterrows():
        post_session = session.query(Post).filter_by(post_id=post.get("PostID")).first()
        if post_session:
            # Don't add post to db if it already exists
            continue
        # Write posts found to db and append to new_posts df
        write_to_db(post, session)
        new_posts = new_posts.append(post)

    return new_posts


def get_session(engine):
    """Build sqlalchemy session."""
    Session = sessionmaker(bind=engine)
    return Session()


def get_engine():
    """Build sqlalchemy engine."""
    engine = create_engine(
        "sqlite:///" + os.path.join(BASE_DIR, "posts", "posts.db") + "?check_same_thread=False",
        echo=False,
    )
    Base.metadata.create_all(engine)

    return engine


def write_to_db(post, session):
    """Link post content and write to database."""
    post_db = Post(
        post_id=post["PostID"],
        title=post["Title"],
        url=post["URL"],
        date=post["DateUpdated"],
        price=post["Price"],
        neighborhood=post["Neighborhood"],
        address=post["Address"],
        housing_type=post["HousingType"],
        laundry=post["Laundry"],
        parking=post["Parking"],
        bedrooms=post["Bedrooms"],
        sqft=post["AreaFt2"],
    )
    session.add(post_db)
    session.commit()


def drop_db():
    """Drop all tables from engine."""
    engine = get_engine()
    Post.__table__.drop(engine)
