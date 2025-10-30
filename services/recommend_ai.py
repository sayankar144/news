from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from services.db_manager import get_articles, get_user

model = SentenceTransformer('paraphrase-MiniLM-L3-v2')

def get_article_embeddings(articles):
    texts = [f"{a.get('title', '')} {a.get('description', '')}" for a in articles]
    embeddings = model.encode(texts)
    return embeddings

def recommend_similar_articles(selected_article, all_articles, top_n=5):
    all_embeddings = get_article_embeddings(all_articles)
    selected_text = f"{selected_article.get('title', '')} {selected_article.get('description', '')}"
    selected_emb = model.encode([selected_text])
    scores = cosine_similarity(selected_emb, all_embeddings)[0]
    top_idx = np.argsort(scores)[::-1][1:top_n + 1]
    return [all_articles[i] for i in top_idx]

def personalized_recommendations(username, top_n=5):
    user = get_user(username)
    article_history = user.get("article_history", [])
    if not article_history:
        return []
    user_texts = [f"{a.get('title', '')} {a.get('description', '')}" for a in article_history]
    user_embeddings = model.encode(user_texts)
    user_profile = np.mean(user_embeddings, axis=0).reshape(1, -1)
    all_articles = get_articles()
    all_embeddings = get_article_embeddings(all_articles)
    similarities = cosine_similarity(user_profile, all_embeddings)[0]
    top_indices = np.argsort(similarities)[::-1]
    read_titles = {a.get("title") for a in article_history}
    recommendations = [all_articles[i] for i in top_indices if all_articles[i].get("title") not in read_titles]
    return recommendations[:top_n]
