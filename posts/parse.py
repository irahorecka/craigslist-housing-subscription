import datetime
import pandas as pd

pd.options.mode.chained_assignment = None


def parse_content(post_content, param={}):
    """Main function to read, clean, process, and generate craigslist housing posts
    within the range and specifications desired by the user."""
    data_cleaning_funcs = [
        rm_repost,
        convert_price_to_int,
        convert_date_to_dttm,
        date_one_week_today,
        sort_time_date,
    ]
    for func in data_cleaning_funcs:
        post_content = func(post_content, param=param)
    return post_content


def rm_repost(dtfm, **kwargs):
    """Remove repost ids."""
    dtfm_no_repost = dtfm.loc[dtfm["RepostID"] == ""]
    dtfm_unique = dtfm.loc[dtfm["RepostID"] != ""].drop_duplicates(subset="RepostID")

    return dtfm_no_repost.append(dtfm_unique)


def convert_price_to_int(dtfm, **kwargs):
    """Convert price values to integers."""
    dtfm["Price"] = dtfm["Price"].str.replace("$", "").str.replace(",", "").astype("int")
    return dtfm


def convert_date_to_dttm(dtfm, **kwargs):
    """Convert date string to datetime object."""
    dtfm["DateUpdated"] = pd.to_datetime(dtfm["DateUpdated"])
    dtfm["TimeUpdated"] = pd.to_datetime(dtfm["TimeUpdated"], format="%H:%M")
    return dtfm


def date_one_week_today(dtfm, **kwargs):
    """Select craigslist posts posted within one week of today."""
    return dtfm[dtfm["DateUpdated"] > datetime.datetime.now() - pd.to_timedelta("7day")]


def sort_time_date(dtfm, **kwargs):
    """Sort posts by time then date - newest posts first."""
    dtfm = dtfm.sort_values(by="TimeUpdated", ascending=False)
    dtfm = dtfm.sort_values(by="DateUpdated", ascending=False)

    return dtfm
