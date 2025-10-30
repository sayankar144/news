import requests
API_KEY = "3555a74b35c2431b8a2753bfd7c442c9"

url = f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={API_KEY}"
res = requests.get(url)
data = res.json()

print("Status:", res.status_code)
print("Total Results:", data.get('totalResults'))
print("First Article:", data['articles'][0]['title'] if data.get('articles') else "No articles found")
