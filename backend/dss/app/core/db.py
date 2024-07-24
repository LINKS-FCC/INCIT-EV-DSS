from pymongo import MongoClient
from pymongo import database

from app.core.config import settings


class DB:
    def __init__(self):
        self.instance = self.get_db()

    def get_db(self) -> database.Database:
        client = MongoClient(settings.mongo_uri)
        db = client[settings.db_name]
        return db
