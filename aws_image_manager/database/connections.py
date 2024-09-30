import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class MakeConnections:
    def __init__(self) -> None:
        self.client = MongoClient(os.getenv("MONGO_URI"))
