# 檔案路徑：database.py
from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import settings

# 初始化為 None，由 main.py 的啟動事件賦值
client: AsyncIOMotorClient = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client.get_default_database()
    print("Successfully connected to MongoDB.")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")