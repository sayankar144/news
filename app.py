from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_session import Session
import random
from services.fetch_news import fetch_news
from services.db_manager import (
    create_user, get_user, log_user_interest,
    get_articles, track_article_read, get_user_recommendations
)
from services.recommend_ai import recommend_similar_articles, personalized_recommendations

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]

    selected_category = request.args.get("category")
    categories = ["technology", "business", "sports", "health", "science"]

    for cat in categories:
        fetch_news(cat)

    personalized_ai = personalized_recommendations(username, top_n=6)
    rec_categories = get_user_recommendations(username)
    category_data = {}

    if selected_category and selected_category in categories:
        log_user_interest(username, selected_category)
        main_articles = get_articles(selected_category)
        category_data[selected_category] = main_articles
    else:
        for cat in categories:
            category_data[cat] = get_articles(cat)

    recommended_articles = []
    for cat in rec_categories:
        recommended_articles.extend(get_articles(cat))
    random.shuffle(recommended_articles)

    return render_template(
    "index.html",
    username=username,
    category_data=category_data,
    recommended=recommended_articles,
    rec_categories=rec_categories,
    personalized=personalized_ai,
    selected_category=selected_category
)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        if create_user(username, password):
            return redirect(url_for("login"))
        return render_template("signup.html", error="Username already exists.")
    return render_template("signup.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user(username)
        if user and bcrypt.check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/read/<title>')
def read_article(title):
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    all_articles = get_articles()
    article = next((a for a in all_articles if a.get("title") == title), None)
    if not article:
        return "Article not found", 404
    track_article_read(username, article)
    return redirect(article.get("url"))

@app.route('/recommend/<title>')
def ai_recommend(title):
    if "username" not in session:
        return redirect(url_for("login"))
    all_articles = get_articles()
    selected = next((a for a in all_articles if a.get("title") == title), None)
    if not selected:
        return render_template("recommend.html", similar=[], title="Not Found")
    similar = recommend_similar_articles(selected, all_articles, top_n=5)
    return render_template("recommend.html", similar=similar, title=selected.get("title"))

@app.route('/history')
def history():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    user = get_user(username)
    history = user.get("article_history", [])

    # Sort by most recent first
    history = sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)

    return render_template("history.html", history=history, username=username)


if __name__ == '__main__':
    from waitress import serve
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Running on port {port}")
    serve(app, host='0.0.0.0', port=port)

