from pymongo import MongoClient

MONGO_URI = "mongodb+srv://sayankar:MyPass123@cluster0.1fc8akd.mongodb.net/news_db?appName=Cluster0"
client = MongoClient(MONGO_URI)

db = client["news_db"]
print("✅ Connected to:", db.name)
print("📂 Collections:", db.list_collection_names())