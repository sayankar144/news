import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
