import os
import socket
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- Configuration ---
TAILSCALE_CLIENT_ID = "your_client_id"
TAILSCALE_CLIENT_SECRET = "your_client_secret"
TAILNET_NAME = "your-tailnet.ts.net"
ANDROID_UDP_PORT = 1780

def get_tailscale_auth_key():
    """Generates a temporary Tailscale Auth Key using OAuth."""
    # 1. Get Access Token
    token_url = "https://login.tailscale.com/api/v2/oauth/token"
    data = {
        'client_id': TAILSCALE_CLIENT_ID,
        'client_secret': TAILSCALE_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, data=data).json()
    access_token = response['access_token']

    # 2. Create Auth Key for a specific tag
    key_url = f"https://api.tailscale.com/api/v2/tailnet/{TAILNET_NAME}/keys"
    key_data = {
        "capabilities": {
            "devices": {
                "create": {
                    "reusable": False,
                    "ephemeral": True,
                    "tags": ["tag:user-device"]
                }
            }
        },
        "expirySeconds": 3600
    }
    res = requests.post(key_url, json=key_data, auth=(access_token, '')).json()
    return res.get('key')

def query_udp_server(ip):
    """Sends a request to the Android UDP server and gets the response."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        sock.sendto(b"GET_DATA", (ip, ANDROID_UDP_PORT))
        data, _ = sock.recvfrom(1024)
        return data.decode('utf-8')
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    # In a real app, you'd check if the user is logged in here
    auth_key = get_tailscale_auth_key()
    return render_template_string('''
        <h1>Connect your Android Device</h1>
        <p>1. Open Tailscale on your Android phone.</p>
        <p>2. Login using the key below (or scan the QR code in your app):</p>
        <pre style="background:#eee; padding:10px;">{{ key }}</pre>
        <hr>
        <form action="/fetch" method="get">
            Enter Phone's Tailscale IP: <input type="text" name="ip">
            <input type="submit" value="Read Android Data">
        </form>
    ''', key=auth_key)

@app.route('/fetch')
def fetch_data():
    device_ip = request.args.get('ip')
    content = query_udp_server(device_ip)
    return f"Data from Android ({device_ip}): {content}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
