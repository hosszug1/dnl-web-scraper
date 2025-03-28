import pymongo
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    def __init__(self, mongo_uri: str, db_name: str) -> None:
        self.client: AsyncIOMotorClient = None
        self.mongo_uri = mongo_uri
        self.db_name = db_name

    @property
    def database(self) -> AsyncIOMotorClient:
        return self.client[self.db_name]

    def get_collection(self, collection_name: str) -> pymongo.collection.Collection:
        return self.database[collection_name]
