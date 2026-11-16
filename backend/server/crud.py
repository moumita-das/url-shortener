from db.client import db_client
from settings import settings

url_map = db_client[settings.mongodb_name]["url_map"]
users_collection = db_client[settings.mongodb_name]["users"]

def insert_url_mapping(short_url, long_url, username=None):
    """Insert a new URL mapping into the database."""
    url_map.insert_one({"short_url": short_url, "long_url": long_url, "user": username})

def get_long_url(short_url):
    """Retrieve the long URL corresponding to the given short URL."""
    mapping = url_map.find_one({"short_url": short_url})
    return mapping

def get_short_url(long_url):
    """Retrieves the short URL"""
    mapping = url_map.find_one({"long_url": long_url})
    return mapping["short_url"] if mapping else None

def delete_url_mapping(short_url):
    """Delete a URL mapping from the database."""
    url_map.delete_one({"short_url": short_url})

def insert_user(username, hashed_password):
    """Insert a new user into the database."""
    users_collection.insert_one({"_id": username, "password": hashed_password})

def get_user(username):
    """Retrieve a user from the database."""
    return users_collection.find_one({"_id": username})