# Serve dashboard.html as a static file for AJAX navigation


import os
import re
from flask import Flask, redirect, request, session, url_for, jsonify, send_from_directory, render_template_string
from markupsafe import Markup
from flask_caching import Cache
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# Configure Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# Discord OAuth2 credentials (set these as environment variables)
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "1404896235785293925")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "https://studious-enigma-jp6g7vv9qwwfrj7-5000.app.github.dev/callback")

DISCORD_API_BASE_URL = "https://discord.com/api"
OAUTH_AUTHORIZE_URL = f"{DISCORD_API_BASE_URL}/oauth2/authorize"
OAUTH_TOKEN_URL = f"{DISCORD_API_BASE_URL}/oauth2/token"
USER_API_URL = f"{DISCORD_API_BASE_URL}/users/@me"

# Serve dashboard.html <main> content for AJAX navigation
@app.route('/dashboard_partial')
def dashboard_partial():
    # Only return the <main>...</main> part of dashboard.html
    with open(os.path.join(os.path.dirname(__file__), "dashboard.html"), encoding="utf-8") as f:
        html = f.read()
    match = re.search(r'<main[\s\S]*?</main>', html, re.IGNORECASE)
    if match:
        return Markup(match.group(0))
    return '', 404

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# Configure Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# Discord OAuth2 credentials (set these as environment variables)
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "1404896235785293925")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "dI73tzXa8pbUJvuELFcVRpiKBPQORnR6")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "https://studious-enigma-jp6g7vv9qwwfrj7-5000.app.github.dev/callback")

DISCORD_API_BASE_URL = "https://discord.com/api"
OAUTH_AUTHORIZE_URL = f"{DISCORD_API_BASE_URL}/oauth2/authorize"
OAUTH_TOKEN_URL = f"{DISCORD_API_BASE_URL}/oauth2/token"
USER_API_URL = f"{DISCORD_API_BASE_URL}/users/@me"

# Serve Index.html as the main page
@app.route("/")
def home():
    with open(os.path.join(os.path.dirname(__file__), "Index.html"), encoding="utf-8") as f:
        html = f.read()
    return render_template_string(html)

@app.route("/login")
def login():
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds"
    }
    url = requests.Request('GET', OAUTH_AUTHORIZE_URL, params=params).prepare().url
    return redirect(url)

@app.route('/dashboard.html')
def dashboard_html():
    return send_from_directory(os.path.dirname(__file__), 'dashboard.html')

@app.route("/callback")
def callback():
    # Handle Discord error responses
    if "error" in request.args:
        return f"Discord OAuth2 error: {request.args['error']}", 400

    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "scope": "identify guilds"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(OAUTH_TOKEN_URL, data=data, headers=headers)
    if resp.status_code != 200:
        return f"Failed to get token: {resp.text}", 400
    token = resp.json().get("access_token")
    if not token:
        return "No access token in response", 400
    session["discord_token"] = token
    return redirect(url_for("home"))

@cache.cached(timeout=60, key_prefix="discord_profile")
@app.route("/profile")
def profile():
    token = session.get("discord_token")
    if not token:
        return redirect(url_for("login"))
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(USER_API_URL, headers=headers)
    if resp.status_code != 200:
        return "Failed to fetch user info", 400
    user = resp.json()
    return jsonify(user)

# Endpoint to get the authenticated user's ID
def get_user_id_from_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    user_url = f"{DISCORD_API_BASE_URL}/users/@me"
    user_resp = requests.get(user_url, headers=headers)
    if user_resp.status_code != 200:
        return None
    return user_resp.json().get("id")


# Minimal /user_guilds endpoint: returns user's servers from Discord
@app.route("/user_guilds")
def user_guilds():
    token = session.get("discord_token")
    if not token:
        return jsonify({"error": "Not authenticated"}), 401
    headers = {"Authorization": f"Bearer {token}"}
    guilds_url = f"{DISCORD_API_BASE_URL}/users/@me/guilds"
    resp = requests.get(guilds_url, headers=headers)
    if resp.status_code != 200:
        return jsonify({"error": "Failed to fetch guilds", "details": resp.text}), 400
    return jsonify(resp.json())

# Serve static files (like dashboard.js, styles.css, etc.)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")