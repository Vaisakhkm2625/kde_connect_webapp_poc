import os
import socket
import uuid
import requests
import qrcode
import base64
from io import BytesIO
from flask import Flask, render_template_string, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TAILNET = os.getenv("TAILNET")
UDP_PORT = 1780


def get_access_token():
    resp = requests.post(
        "https://login.tailscale.com/api/v2/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
    ).json()
    return resp["access_token"]


def create_auth_key(tags, reusable=False, ephemeral=True, expiry_seconds=3600):
    access_token = get_access_token()
    
    url = f"https://api.tailscale.com/api/v2/tailnet/{TAILNET}/keys"
    
    payload = {
        "capabilities": {
            "devices": {
                "create": {
                    "reusable": reusable,
                    "ephemeral": ephemeral,
                    "tags": tags,
                    "preauthorized": True,          # auto-approve → device joins without manual review
                }
            }
        },
        "expirySeconds": expiry_seconds,
        # description omitted on purpose — avoids the invalid characters error
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    
    res = requests.post(url, json=payload, headers=headers)
    
    print("Auth key creation status:", res.status_code)
    print("Response:", res.text)
    
    if res.status_code not in (200, 201):
        raise Exception(f"Failed to create auth key: {res.status_code} - {res.text}")
    
    data = res.json()
    
    key = data.get("key")
    if not key:
        raise Exception(f"No 'key' in response: {data}")
    
    return key

def update_acl(client_tag, server_tag):
    token = get_access_token()
    url = f"https://api.tailscale.com/api/v2/tailnet/{TAILNET}/acl"

    # Get current ACL
    acl = requests.get(url, auth=(token, "")).json()

    # Add 1:1 rule
    acl.setdefault("acls", []).append(
        {"action": "accept", "src": [client_tag], "dst": [f"{server_tag}:*"]}
    )

    # Allow this app to use the new tags
    tag_owners = acl.setdefault("tagOwners", {})
    tag_owners[client_tag] = ["autogroup:admin"]
    tag_owners[server_tag] = ["autogroup:admin"]

    # Push updated ACL
    requests.post(url, json=acl, auth=(token, ""))


def generate_qr(text):
    img = qrcode.make(text)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


@app.route("/")
def home():
    session_id = uuid.uuid4().hex[:8]

    client_tag = f"tag:android-{session_id}"
    server_tag = f"tag:server-{session_id}"

    client_key = create_auth_key([client_tag], reusable=False, ephemeral=True, expiry_seconds=3600)
    server_key = create_auth_key(
        [server_tag], reusable=True, ephemeral=False, expiry_seconds=3600 * 24 * 30  # 30 days
    )

    update_acl(client_tag, server_tag)

    qr_base64 = generate_qr(client_key)

    html = f"""
    <html>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h2>New Isolated Pair Created</h2>
            <p><strong>Session ID:</strong> {session_id}</p>

            <h3>1. Android Device (client)</h3>
            <p>Open Tailscale → Log in with Auth Key → Scan:</p>
            <img src="data:image/png;base64,{qr_base64}" style="border: 1px solid #ccc; padding: 10px; max-width: 300px;">
            <p style="background:#eee; display:inline-block; padding:10px; word-break:break-all;">
                <code>{client_key}</code>
            </p>

            <hr>

            <h3>2. Corresponding Virtual Server</h3>
            <p>Run your script with this auth key:</p>
            <p style="background:#eee; display:inline-block; padding:10px; word-break:break-all;">
                <code>{server_key}</code>
            </p>
            <p><strong>Command example:</strong></p>
            <pre style="background:#eee; padding:10px; text-align:left; display:inline-block;">
python add_virtualdevice_to_tailscale.py --authkey {server_key}
            </pre>
            <p>(Your script no longer needs to create a key — just use the one above and do <code>tailscale up --authkey=...</code> inside it.)</p>

            <hr>
            <h3>Test UDP from Android</h3>
            <form action="/query" method="get">
                Android Tailscale IP: <input type="text" name="ip" placeholder="100.x.y.z" style="width:180px;">
                <button type="submit">Send GET_DATA</button>
            </form>

            <p style="margin-top:40px; color:#666; font-size:0.9em;">
                Every refresh = new isolated pair. ACL updated automatically.
            </p>
        </body>
    </html>
    """
    return render_template_string(html)


@app.route("/query")
def query():
    ip = request.args.get("ip")
    if not ip:
        return "<h3>Error: no IP</h3><a href='/'>Back</a>"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3.0)
        sock.sendto(b"GET_DATA", (ip, UDP_PORT))
        data, _ = sock.recvfrom(1024)
        return f"<h3>Response from {ip}:</h3><pre>{data.decode(errors='ignore')}</pre><a href='/'>Back</a>"
    except Exception as e:
        return f"<h3>Error:</h3><p>{str(e)}</p><a href='/'>Back</a>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
