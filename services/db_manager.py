from pymongo import MongoClient
from config import MONGO_URI
from datetime import datetime
from collections import Counter

client = MongoClient(MONGO_URI)
db = client["news_db"]
articles = db["articles"]
users = db["users"]

def insert_article(article):
    if article and article.get("title"):
        if not articles.find_one({"title": article["title"]}):
            articles.insert_one(article)

def get_articles(category=None):
    query = {"category": category} if category else {}
    return list(articles.find(query))

def create_user(username, hashed_pw):
    if users.find_one({"username": username}):
        return False
    users.insert_one({
        "username": username,
        "password": hashed_pw,
        "click_history": [],
        "article_history": []
    })
    return True

def get_user(username):
    return users.find_one({"username": username})

def log_user_interest(username, category):
    users.update_one(
        {"username": username},
        {"$push": {"click_history": {"category": category, "timestamp": datetime.now()}}},
        upsert=True
    )

from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["news_db"]
users = db["users"]

def track_article_read(username, article):
    entry = {
        "title": article.get("title", "Untitled Article"),
        "url": article.get("url", "#"),
        "category": article.get("category", "general"),
        "image": article.get("image") or "https://via.placeholder.com/400x200?text=No+Image",
        "description": article.get("description", "No description available."),
        "timestamp": datetime.now()
    }

    users.update_one(
        {"username": username},
        {"$push": {"article_history": entry}},
        upsert=True
    )


def get_user_recommendations(username):
    user = users.find_one({"username": username})
    if not user or "click_history" not in user:
        return ["technology"]
    categories = [c["category"] for c in user["click_history"]]
    most_common = [cat for cat, _ in Counter(categories).most_common(2)]
    return most_common
