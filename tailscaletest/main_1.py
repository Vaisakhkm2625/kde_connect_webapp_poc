import os
import socket
import requests
import qrcode
import base64
from io import BytesIO
from flask import Flask, render_template_string, request

app = Flask(__name__)

# --- Configuration (Use Environment Variables in Production) ---

CLIENT_ID = "k9eXfqB9VA11CNTRL"
CLIENT_SECRET = "tskey-client-k9eXfqB9VA11CNTRL-hHVbwX6YZnRURwpZ3rbKnR1ita3CLkdy"

TAILNET = "tail25360.ts.net"  # Found in Tailscale Settings > General
UDP_PORT = 1780

def get_auth_key():
    """Fetches an OAuth token and creates a tagged Auth Key."""
    # Step 1: Get Access Token
    token_response = requests.post(
        "https://login.tailscale.com/api/v2/oauth/token",
        data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "client_credentials"}
    ).json()
    print(token_response)
    access_token = token_response.get("access_token")

    # Step 2: Create Auth Key
    key_url = f"https://api.tailscale.com/api/v2/tailnet/{TAILNET}/keys"
    payload = {
        "capabilities": {
            "devices": {
                "create": {
                    "reusable": False,
                    "ephemeral": True,
                    "tags": ["tag:kcuser1"]
                    #"tags": ["tag:user-device"]
                }
            }
        },
        "expirySeconds": 3600 # Key lasts 1 hour
    }
    key_res = requests.post(key_url, json=payload, auth=(access_token, '')).json()
    print(key_res)
    return key_res.get("key")

def generate_qr(text):
    """Converts text to a base64 encoded PNG image."""
    img = qrcode.make(text)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode('ascii')

@app.route('/')
def home():
    auth_key = get_auth_key()
    qr_base64 = generate_qr(auth_key)
    
    html = '''
    <html>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h2>Connect Your Android Device</h2>
            <p>1. Open Tailscale on Android</p>
            <p>2. Select "Log in with Auth Key" and scan/enter this:</p>
            <img src="data:image/png;base64,{{qr}}" style="border: 1px solid #ccc; padding: 10px;">
            <p style="background:#eee; display:inline-block; padding:10px;"><code>{{key}}</code></p>
            <hr>
            <h3>Query Device</h3>
            <form action="/query" method="get">
                Device Tailscale IP: <input type="text" name="ip" placeholder="100.x.y.z">
                <button type="submit">Fetch UDP Data</button>
            </form>
        </body>
    </html>
    '''
    return render_template_string(html, qr=qr_base64, key=auth_key)

@app.route('/query')
def query():
    ip = request.args.get('ip')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3.0)
        sock.sendto(b"GET_DATA", (ip, UDP_PORT))
        data, _ = sock.recvfrom(1024)
        return f"<h3>Response from {ip}:</h3><pre>{data.decode()}</pre><a href='/'>Back</a>"
    except Exception as e:
        return f"<h3>Error:</h3><p>{str(e)}</p><a href='/'>Back</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
