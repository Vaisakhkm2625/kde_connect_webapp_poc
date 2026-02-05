from flask import Flask, render_template_string, request, jsonify
import subprocess
import segno
import io
import base64
import logging
import datetime
import os

app = Flask(__name__)

# Setup logging
logging.basicConfig(filename='wireguard_connections.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def get_wg_keys():
    # Uses 'wg' from the nix-shell buildInputs
    priv_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    pub_key = subprocess.check_output(["sh", "-c", f"echo {priv_key} | wg pubkey"]).decode().strip()
    print({priv_key, pub_key})
    return priv_key, pub_key

def add_client_to_server(pub_key, client_ip="10.0.1.2"):
    """Automatically add client to WireGuard server"""
    try:
        # Add the client peer to the server
        subprocess.run(["sudo", "wg", "set", "server", "peer", pub_key, "allowed-ips", f"{client_ip}/32"], check=True)
        subprocess.run(["sudo", "wg-quick", "save", "server"], check=True)
        
        # Log the addition
        logging.info(f"Client added with public key: {pub_key}")
        print(f"[{datetime.datetime.now()}] Client added: {pub_key}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to add client {pub_key}: {e}")
        print(f"[{datetime.datetime.now()}] Failed to add client: {e}")
        return False
    # Uses 'wg' from the nix-shell buildInputs
    priv_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    pub_key = subprocess.check_output(["sh", "-c", f"echo {priv_key} | wg pubkey"]).decode().strip()
    print({priv_key, pub_key})
    return priv_key, pub_key

@app.route('/')
def index():
    priv, pub = get_wg_keys()
    
    # Get server's local IP for endpoint
    import socket
    server_ip = socket.gethostbyname(socket.gethostname())
    
    # Phone Client Config
    config = f"""[Interface]
PrivateKey = {priv}
Address = 10.0.1.2/32
DNS = 1.1.1.1

[Peer]
PublicKey = 
Endpoint = {server_ip}:8096
AllowedIPs = 0.0.0.0/0"""

    # Auto-add client to server
    if add_client_to_server(pub):
        status = "✅ Client auto-added to server"
    else:
        status = "❌ Failed to add client to server"

    # Generate QR as base64 to display directly in HTML
    qr = segno.make(config)
    out = io.BytesIO()
    qr.save(out, kind='png', scale=5)
    encoded = base64.b64encode(out.getvalue()).decode('utf-8')
    
    return render_template_string('''
        <h1>Your WireGuard Config</h1>
        <p><strong>{{status}}</strong></p>
        <img src="data:image/png;base64,{{img}}">
        <p>Public Key: <code>{{pub}}</code></p>
        <p><a href="/status">Check Connection Status</a></p>
    ''', img=encoded, pub=pub, status=status)

@app.route('/status')
def status():
    """Check WireGuard connection status"""
    try:
        result = subprocess.run(["sudo", "wg", "show", "server"], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout
            lines = output.split('\n')
            peer_info = []
            current_peer = None
            
            for line in lines:
                if line.startswith('peer:'):
                    current_peer = line.split(': ')[1]
                elif line.startswith('  latest handshake:') and current_peer:
                    peer_info.append(f"Peer {current_peer[:16]}...: {line.strip()}")
            
            if peer_info:
                return render_template_string('''
                    <h1>WireGuard Connections</h1>
                    <ul>
                        {% for peer in peers %}
                        <li>{{ peer }}</li>
                        {% endfor %}
                    </ul>
                    <p><a href="/">Back to Config</a></p>
                ''', peers=peer_info)
            else:
                return render_template_string('''
                    <h1>WireGuard Connections</h1>
                    <p>No active connections found</p>
                    <p><a href="/">Back to Config</a></p>
                ''')
        else:
            return f"Error checking status: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
