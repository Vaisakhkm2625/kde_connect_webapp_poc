from flask import Flask, render_template_string
import subprocess
import segno
import io
import base64

app = Flask(__name__)

def get_wg_keys():
    # Uses 'wg' from the nix-shell buildInputs
    priv_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    pub_key = subprocess.check_output(["sh", "-c", f"echo {priv_key} | wg pubkey"]).decode().strip()
    print({priv_key, pub_key})
    return priv_key, pub_key

@app.route('/')
def index():
    priv, pub = get_wg_keys()
    
    # Example Config
    config = f"""[Interface]
PrivateKey = {priv}
Address = 10.0.1.1/32
DNS = 1.1.1.1

[Peer]
PublicKey = SERVER_PUBLIC_KEY_HERE
Endpoint = your.server.com:51820
AllowedIPs = 0.0.0.0/0"""

    # Generate QR as base64 to display directly in HTML
    qr = segno.make(config)
    out = io.BytesIO()
    qr.save(out, kind='png', scale=5)
    encoded = base64.b64encode(out.getvalue()).decode('utf-8')
    
    return render_template_string('''
        <h1>Your WireGuard Config</h1>
        <img src="data:image/png;base64,{{img}}">
        <p>Public Key to add to server: <code>{{pub}}</code></p>
    ''', img=encoded, pub=pub)

if __name__ == '__main__':
    app.run(port=5000)
