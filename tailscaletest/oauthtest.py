import os
import time
import requests
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

TAILSCALE_CLIENT_ID = os.environ["TAILSCALE_CLIENT_ID"]
TAILSCALE_CLIENT_SECRET = os.environ["TAILSCALE_CLIENT_SECRET"]
TAILNET = os.environ["TAILNET"]

# ---- DEMO USER STORE (replace with DB later) ----
USERS = {
    "alice": "password123",
    "bob": "hunter2"
}

# ---- OAuth token cache ----
_oauth_token = None
_oauth_expiry = 0


def get_oauth_token():
    global _oauth_token, _oauth_expiry

    if _oauth_token and time.time() < _oauth_expiry:
        return _oauth_token

    r = requests.post(
        "https://api.tailscale.com/api/v2/oauth/token",
        data={
            "client_id": TAILSCALE_CLIENT_ID,
            "client_secret": TAILSCALE_CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "auth_keys"
        }
    )
    r.raise_for_status()

    data = r.json()
    _oauth_token = data["access_token"]
    _oauth_expiry = time.time() + data.get("expires_in", 3600) - 60
    return _oauth_token


def create_auth_key(username):
    token = get_oauth_token()

    payload = {
        "capabilities": {
            "devices": {
                "create": {
                    "reusable": False,
                    "ephemeral": False,
                    "tags": [f"tag:user-{username}"]
                }
            }
        },
        "expirySeconds": 3600
    }

    r = requests.post(
        f"https://api.tailscale.com/api/v2/tailnet/{TAILNET}/keys",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    r.raise_for_status()
    return r.json()["key"]


# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        if USERS.get(user) == pw:
            session["user"] = user
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    auth_key = None
    if request.method == "POST":
        auth_key = create_auth_key(session["user"])

    return render_template("dashboard.html", user=session["user"], auth_key=auth_key)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
