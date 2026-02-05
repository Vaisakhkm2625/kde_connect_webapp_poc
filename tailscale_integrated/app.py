import base64
from io import BytesIO
import os
import time
import uuid
import threading
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from isolation_manager import IsolationManager
import qrcode

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TAILNET = os.getenv("TAILNET")

if not all([CLIENT_ID, CLIENT_SECRET, TAILNET]):
    print("Missing required environment variables: CLIENT_ID, CLIENT_SECRET, TAILNET")

# Global manager
manager = IsolationManager(CLIENT_ID, CLIENT_SECRET, TAILNET)

# Store active sessions/namespaces
# Structure: { session_id: { 'ns_name': str, 'status': str, 'url': str, 'procs': [], 'auth_key': str, 'qr_base64': str } }
active_instances = {}

def generate_qr(text):
    """Converts text to a base64 encoded PNG image."""
    img = qrcode.make(text)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode('ascii')

@app.route('/')
def home():
    """Home page showing current status and login button."""
    user_session = session.get('user_session')
    instance = active_instances.get(user_session)
    
    html = '''
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <title>KDE Connect - Tailscale Isolation</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                :root {
                    --color-kde-blue: #3daee9;
                    --color-kde-bg: #1b1e20;
                    --color-kde-card: #232629;
                    --color-kde-border: #31363b;
                    --color-kde-text: #eff0f1;
                    --color-kde-text-dim: #bdc3c7;
                    --color-kde-danger: #ed1515;
                    --color-kde-success: #11d116;
                    --color-kde-warning: #f67400;
                    --font-sans: Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                }
                
                body {
                    background-color: var(--color-kde-bg);
                    color: var(--color-kde-text);
                    font-family: var(--font-sans);
                    margin: 0;
                    height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .container {
                    background-color: var(--color-kde-card);
                    border: 1px solid var(--color-kde-border);
                    border-radius: 8px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                    padding: 40px;
                    width: 100%;
                    max-width: 500px;
                    text-align: center;
                }
                
                h1 {
                    font-size: 24px;
                    margin-bottom: 30px;
                    color: var(--color-kde-blue);
                }
                
                .status-box {
                    background-color: rgba(61, 174, 233, 0.1);
                    border: 1px solid var(--color-kde-blue);
                    border-radius: 6px;
                    padding: 20px;
                    margin-bottom: 20px;
                    text-align: left;
                }
                
                .status-box.success {
                    border-color: var(--color-kde-success);
                    background-color: rgba(17, 209, 22, 0.1);
                }
                
                .status-label {
                    color: var(--color-kde-text-dim);
                    font-size: 0.9em;
                    margin-bottom: 5px;
                }
                
                .status-value {
                    font-weight: bold;
                    margin-bottom: 15px;
                }
                
                .qr-section {
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    color: #000;
                }
                
                code {
                    background-color: rgba(255, 255, 255, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-family: monospace;
                    word-break: break-all;
                }
                
                .qr-section code {
                    background-color: #eee;
                    color: #333;
                }

                a { color: var(--color-kde-blue); text-decoration: none; }
                a:hover { text-decoration: underline; }

                button {
                    background-color: var(--color-kde-blue);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: opacity 0.2s;
                    width: 100%;
                    font-weight: 600;
                }
                
                button:hover { opacity: 0.9; }
                
                button.cancel {
                    background-color: var(--color-kde-danger);
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>KDE Connect Isolation</h1>
                
                {% if instance %}
                    <div class="status-box {% if instance.url %}success{% endif %}">
                        <div class="status-label">Status</div>
                        <div class="status-value">{{ instance.status }}</div>
                        
                        {% if instance.ns_name %}
                            <div class="status-label">Namespace</div>
                            <div class="status-value"><code>{{ instance.ns_name }}</code></div>
                        {% endif %}
                        
                        {% if instance.url %}
                            <div class="status-label">Public Access</div>
                            <div class="status-value">
                                <a href="{{ instance.url }}" target="_blank" style="text-decoration: none;">
                                    <button type="button" style="background-color: var(--color-kde-success);">Connect</button>
                                </a>
                            </div>
                        {% endif %}
                    </div>
                    
                    {% if instance.qr_base64 %}
                        <div class="qr-section">
                            <h3 style="margin-top:0">Connect Device</h3>
                            <p style="font-size: 0.9em; color: #666;">Scan with Tailscale App</p>
                            <img src="data:image/png;base64,{{ instance.qr_base64 }}" style="width: 180px; height: 180px;">
                            <div style="margin-top: 10px;">
                                <code>{{ instance.auth_key }}</code>
                            </div>
                        </div>
                    {% endif %}
                    
                    <form action="/stop" method="post">
                        <button type="submit" class="cancel">Stop & Cleanup</button>
                    </form>
                {% else %}
                    <p style="margin-bottom: 30px; color: var(--color-kde-text-dim);">
                        Authenticate to start a secure, isolated KDE Connect instance accessible via Tailscale Funnel.
                    </p>
                    <form action="/login" method="post">
                        <button type="submit">Start Isolated Service</button>
                    </form>
                {% endif %}
            </div>
        </body>
    </html>
    '''
    return render_template_string(html, instance=instance)

@app.route('/login', methods=['POST'])
def login():
    """Simulate login and start the setup process."""
    session_id = str(uuid.uuid4())
    session['user_session'] = session_id
    
    ns_name = f"ns-{session_id[:8]}"
    
    # Generate key synchronously so we can show it immediately
    try:
        # Using valid static tags as per main_login_tailscale.py
        tags = ["tag:kcuser1", "tag:kcadmin"] 
        auth_key = manager.get_auth_key(tags=tags)
        qr_base64 = generate_qr(auth_key)
        
        active_instances[session_id] = {
            'ns_name': ns_name,
            'status': 'Initializing...',
            'url': None,
            'procs': [],
            'auth_key': auth_key,
            'qr_base64': qr_base64
        }
        
        # Run setup in background
        thread = threading.Thread(target=run_setup_flow, args=(session_id, ns_name, auth_key))
        thread.start()
        
    except Exception as e:
        print(f"Login setup failed: {e}")
        # In a real app flip a flash message, here just redirect and show error in status or empty
        pass

    return redirect(url_for('home'))

@app.route('/stop', methods=['POST'])
def stop():
    """Stop the instance and cleanup."""
    session_id = session.get('user_session')
    if session_id and session_id in active_instances:
        instance = active_instances[session_id]
        ns_name = instance['ns_name']
        
        # Kill processes
        for proc in instance['procs']:
            if proc:
                proc.terminate()
        
        # Cleanup namespace
        try:
            manager.cleanup(ns_name)
        except Exception as e:
            print(f"Error cleaning up: {e}")
            
        del active_instances[session_id]
        session.pop('user_session', None)
        
    return redirect(url_for('home'))

def run_setup_flow(session_id, ns_name, auth_key):
    """Background task to run the creation logic."""
    try:
        instance = active_instances.get(session_id)
        if not instance:
            return

        # 1. (Valid Auth Key already generated)
        
        # 2. Setup Namespace
        instance['status'] = 'Setting up Network Namespace...'
        manager.setup_namespace(ns_name)
        
        # 3. Start KDE Connect Server
        instance['status'] = 'Starting KDE Connect Server...'
        server_proc = manager.start_kdeconnect(ns_name)
        instance['procs'].append(server_proc)
        
        # 4. Join Tailscale (using the shared key)
        instance['status'] = 'Joining Tailscale...'
        tailscaled_proc = manager.join_tailscale(ns_name, auth_key)
        instance['procs'].append(tailscaled_proc)
        
        # 5. Enable Funnel
        instance['status'] = 'Enabling Funnel (this takes a moment)...'
        public_url = manager.enable_funnel(ns_name)
        
        instance['url'] = public_url
        instance['status'] = 'Running'
        
    except Exception as e:
        print(f"Setup failed: {e}")
        if session_id in active_instances:
            active_instances[session_id]['status'] = f"Failed: {str(e)}"

if __name__ == '__main__':
    # Ensure running with sudo usually required for network namespaces
    if os.geteuid() != 0:
        print("WARNING: This application likely needs root privileges to manage network namespaces.")
        print("Try running with: sudo python3 app.py")
        
    app.run(host='0.0.0.0', port=5000, debug=True)
