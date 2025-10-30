from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from services.db_manager import get_articles, get_user

# ✅ Initialize a global TF-IDF vectorizer (fast and light)
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)

# ------------------------------------------------------------
# Get TF-IDF embeddings for a list of articles
# ------------------------------------------------------------
def get_article_embeddings(articles):
    texts = [f"{a.get('title', '')} {a.get('description', '')}" for a in articles]
    if not texts:
        return np.array([])
    tfidf_matrix = vectorizer.fit_transform(texts)
    return tfidf_matrix

# ------------------------------------------------------------
# Recommend similar articles (content-based)
# ------------------------------------------------------------
def recommend_similar_articles(selected_article, all_articles, top_n=5):
    if not all_articles or not selected_article:
        return []

    texts = [f"{a.get('title', '')} {a.get('description', '')}" for a in all_articles]
    tfidf_matrix = vectorizer.fit_transform(texts)

    selected_text = f"{selected_article.get('title', '')} {selected_article.get('description', '')}"
    selected_vec = vectorizer.transform([selected_text])

    similarities = cosine_similarity(selected_vec, tfidf_matrix).flatten()
    top_idx = np.argsort(similarities)[::-1][1:top_n + 1]
    return [all_articles[i] for i in top_idx]

# ------------------------------------------------------------
# Personalized recommendations based on user’s reading history
# ------------------------------------------------------------
def personalized_recommendations(username, top_n=5):
    user = get_user(username)
    article_history = user.get("article_history", [])
    if not article_history:
        return []

    # Combine user reading history into a profile text
    user_texts = [f"{a.get('title', '')} {a.get('description', '')}" for a in article_history]
    user_corpus = " ".join(user_texts)

    all_articles = get_articles()
    if not all_articles:
        return []

    # Build TF-IDF matrix for all articles
    texts = [f"{a.get('title', '')} {a.get('description', '')}" for a in all_articles]
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Transform user profile into vector
    user_vec = vectorizer.transform([user_corpus])

    # Calculate cosine similarity between user profile and all articles
    similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()

    # Exclude already read articles
    read_titles = {a.get("title") for a in article_history}
    sorted_indices = np.argsort(similarities)[::-1]
    recommendations = [
        all_articles[i] for i in sorted_indices
        if all_articles[i].get("title") not in read_titles
    ]
    return recommendations[:top_n]
