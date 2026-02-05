import base64
import io
import sys
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
from twisted.web import server, resource
from twisted.internet import reactor
import qrcode

# ======================
#  Configuration
# ======================
SERVER_PRIVATE_KEY = ""   # Change this!
SERVER_PUBLIC_KEY  = ""     # Derived or known

SERVER_ENDPOINT    = "192.168.1.10:51820"         # Your external endpoint
SERVER_INTERFACE   = "wg0"
CLIENT_DNS         = "1.1.1.1, 8.8.8.8"                       # Optional
ALLOWED_IPS        = "0.0.0.0/0, ::/0"                        # Route all traffic

# Start client IP allocation from this (e.g. 10.66.66.2, .3, ...)
BASE_IP = "10.66.66."
NEXT_CLIENT_ID = 2   # Increment for each new client

# ======================
#  Key Generation Helpers
# ======================
def generate_keypair():
    private_key = x25519.X25519PrivateKey.generate()
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_b64 = base64.b64encode(priv_bytes).decode('ascii')

    public_key = private_key.public_key()
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_b64 = base64.b64encode(pub_bytes).decode('ascii')

    return private_b64, public_b64

# ======================
#  Global state (in-memory client counter)
# ======================
client_counter = NEXT_CLIENT_ID

def get_next_client_ip():
    global client_counter
    ip = f"{BASE_IP}{client_counter}"
    client_counter += 1
    return ip

# ======================
#  HTML + QR Resource
# ======================
class QRResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        global client_counter

        # Generate new client
        client_priv, client_pub = generate_keypair()
        client_ip = get_next_client_ip()

        # Client config
        config = f"""[Interface]
PrivateKey = {client_priv}
Address = {client_ip}/32
DNS = {CLIENT_DNS}

[Peer]
PublicKey = {SERVER_PUBLIC_KEY}
AllowedIPs = {ALLOWED_IPS}
Endpoint = {SERVER_ENDPOINT}
PersistentKeepalive = 25
"""

        # Print to console so you can add to server config
        print("\n" + "="*60)
        print(f"New client generated (ID {client_counter-1}): {client_ip}/32")
        print("Add this to your server /etc/wireguard/wg0.conf under [Peer]:")
        print(f"[Peer]")
        print(f"PublicKey = {client_pub}")
        print(f"AllowedIPs = {client_ip}/32")
        print("Then run: wg syncconf wg0 <(wg-quick strip wg0)")
        print("or restart the interface.")
        print("="*60 + "\n")

        # Generate QR code in memory
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(config)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to bytes
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('ascii')

        # Simple HTML response
        html = f"""<html>
<head><title>WireGuard Client QR Code</title></head>
<body style="font-family: monospace; text-align:center; background:#f0f0f0;">
<h2>New WireGuard Client Config</h2>
<p>Scan this QR code with the WireGuard app on your phone.</p>
<img src="data:image/png;base64,{img_str}" alt="QR Code" style="width:300px; height:300px;"/>
<h3>Config (for manual import if needed)</h3>
<pre style="background:#fff; padding:15px; border:1px solid #ccc; display:inline-block; text-align:left;">{config}</pre>
<p><small>Client IP: {client_ip}/32 | Refresh page for new client.</small></p>
</body>
</html>"""

        request.setHeader(b"Content-Type", b"text/html; charset=utf-8")
        return html.encode('utf-8')

# ======================
#  Startup
# ======================
print("Zero-config WireGuard QR server starting...")
print(f"Server PublicKey (for reference): {SERVER_PUBLIC_KEY}")
print(f"Access http://localhost:8080/ (or your IP:8080) to generate client QR codes.")
print("Each refresh = new client. Add printed [Peer] to your real wg0.conf!")

root = resource.Resource()
root.putChild(b"", QRResource())
site = server.Site(root)

reactor.listenTCP(8080, site)
reactor.run()
