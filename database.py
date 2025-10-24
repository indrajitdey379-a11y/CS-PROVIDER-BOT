# database.py
import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(Config.DATABASE_URL)
        self.db = self._client["StreamLinksDB"]
        self.collection = self.db["links"]

    async def save_link(self, unique_id, message_id):
        await self.collection.insert_one({'_id': unique_id, 'message_id': message_id})

    async def get_link(self, unique_id):
        doc = await self.collection.find_one({'_id': unique_id})
        return doc['message_id'] if doc else None

db = Database()
