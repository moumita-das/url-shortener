from pymongo import MongoClient

from settings import settings


class DBClient:
    def __init__(self):
        self.db_url = settings.mongodb_url
        self.client = MongoClient(self.db_url)
        # self._ping()

    def _ping(self):
        try:
            self.client.admin.command('ping')
            print("Connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")


db_client = DBClient().client
