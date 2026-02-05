import json
import threading
import time
import subprocess
import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pydbus import SessionBus
from gi.repository import GLib

# Initialize Flask App
app = Flask(__name__)
# Enable CORS for all routes, allowing requests from the SvelteKit frontend
CORS(app)

# --- Shared State for Notifications ---
# We'll use a queue or list to store recent notifications for the SSE stream
# For simplicity in this mock, we'll just broadcast them as they come.
notification_subscribers = []

def broadcast_notification(data):
    """Sends a notification to all connected SSE clients."""
    # SSE format: "data: <json>\n\n"
    message = f"data: {json.dumps(data)}\n\n"
    # Iterate over a copy of the list to allow modification during iteration if needed
    for q in notification_subscribers[:]:
        try:
            q.put(message)
        except Exception:
            notification_subscribers.remove(q)

# --- DBus Listener for System Notifications ---
def notification_listener_thread():
    """connects to DBus and listens for notifications."""
    try:
        bus = SessionBus()
        # The standard FreeDesktop notification interface
        # We want to monitor signals. simpler approach: use pydbus to subscribe.
        
        # Note: subscribing to all notifications can be tricky depending on the notification server.
        # Often, we can't easily "spy" on other notifications unless we are the notification server.
        # However, for a user session, we might be able to intercept 'Notify' signals if allowed.
        # Alternatively, we can just use this thread to emit *mock* system events if easier, 
        # but let's try to inspect the bus.
        
        # Actually, standard `notify-send` sends TO the notification server.
        # To SEE them, we'd need to be a monitor using `dbus-monitor` equivalent or replace the server.
        # A safer mock interactions for "System -> Frontend" might be to just listen for 
        # our OWN notifications or provide a "Test System Notification" button in the backend 
        # (which we can simulate via an endpoint).
        
        # BUT the prompt asks: "frontend should be able to see notification came in system".
        # Real system notification spying needs `eavesdrop=true` match rule on the message bus.
        # pydbus makes this a bit abstract. 
        
        # Let's try a robust fallback: simpler DBus signal subscription or just a polling loop 
        # that simulates it for this "mock" server if real interception is too complex for a single script.
        # HOWEVER, let's try to do it right with a DBus match rule if possible.
        
        # For now, to keep it stable and "mock-like", I'll implement a helper to Broadcast 
        # "simulated" system events if real eavesdropping is flaky, AND try to attach to the bus.
        
        pass 
    except Exception as e:
        print(f"Error in notification listener: {e}")

# We will use a dedicated Queue for each subscriber
import queue

# --- Endpoints ---

@app.route('/api/notifications', methods=['POST'])
def send_notification():
    """
    Frontend sends notification to System.
    Uses `notify-send`.
    """
    data = request.json
    title = data.get('title', 'KDE Connect Webapp')
    body = data.get('body', '')
    
    try:
        cmd = ['notify-send', title, body]
        subprocess.run(cmd, check=True)
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/stream')
def stream_notifications():
    """
    SSE Stream for notifications (System -> Frontend).
    """
    def event_stream():
        q = queue.Queue()
        notification_subscribers.append(q)
        try:
            while True:
                msg = q.get() # blocks until data is available
                yield msg
        except GeneratorExit:
            notification_subscribers.remove(q)

    return Response(event_stream(), mimetype="text/event-stream")

# --- DBus Monitoring Implementation ---
def monitor_dbus_notifications():
    """
    Runs dbus-monitor to capture notifications.
    Parses output and broadcasts to SSE stream.
    """
    # Monitor 'Notify' method calls on the Notifications interface
    cmd = ['dbus-monitor', "interface='org.freedesktop.Notifications',member='Notify'"]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Simple state machine to capture relevant lines
    # Example output structure:
    # method call time=...
    #    string "app_name"
    #    uint32 id
    #    string "icon"
    #    string "SUMMARY"
    #    string "BODY"
    #    ...
    
    current_lines = []
    
    try:
        for line in iter(proc.stdout.readline, ''):
            line = line.strip()
            if line.startswith("method call"):
                # New notification request started, process previous if valid
                if len(current_lines) >= 6:
                     # Very naive parsing based on position. 
                     # Index 3 is usually summary, 4 is body in the args list
                     # This depends heavily on dbus-monitor output format stability, but works for mock.
                     try:
                         # Extraction logic would go here. For now, we just notify that "something came"
                         # to avoid complex parsing in this mock script.
                         # A better way is to use the `pydbus` library to *listen* but that requires
                         # the script to be the server or use match rules which are tricky to set up simply.
                         
                         # Let's just broadcast a generic event for now, or try to extract strings.
                         pass
                     except:
                         pass
                current_lines = []
                
            if line.startswith("string"):
                # "string \"The Title\"" -> The Title
                content = line[len("string "):].strip('"')
                current_lines.append(content)
                
                # If we have enough lines, let's try to guess the notification
                # structure: app_name, replaces_id, icon, summary, body
                if len(current_lines) == 5:
                    summary = current_lines[3]
                    body = current_lines[4]
                    broadcast_notification({
                        "source": "system",
                        "title": summary,
                        "body": body,
                        "appName": current_lines[0]
                    })

    except Exception as e:
        print(f"DBus monitor error: {e}")
    finally:
        proc.kill()

# --- File Browser Endpoints ---

@app.route('/api/files', methods=['GET'])
def list_files():
    """
    List files in a directory.
    Query param: `path` (default: ~)
    """
    req_path = request.args.get('path', os.path.expanduser('~'))
    
    # Security: basic prevention of going outside allowed areas if needed, 
    # but for a local mock tool, we usually allow full access.
    # Let's just ensure it exists.
    if not os.path.exists(req_path):
        return jsonify({"error": "Path not found"}), 404
        
    if not os.path.isdir(req_path):
        return jsonify({"error": "Not a directory"}), 400

    items = []
    try:
        for entry in os.scandir(req_path):
            try:
                stat = entry.stat()
                items.append({
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "path": entry.path
                })
            except PermissionError:
                continue
    except PermissionError:
        return jsonify({"error": "Permission denied"}), 403

    # Sort: Directories first, then files
    items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
    
    return jsonify({
        "current_path": req_path,
        "items": items
    })

# --- Clipboard Endpoints ---

@app.route('/api/clipboard', methods=['GET'])
def get_clipboard():
    try:
        # wl-paste returns the content of the clipboard
        result = subprocess.run(['wl-paste'], stdout=subprocess.PIPE, text=True, check=True)
        return jsonify({"content": result.stdout})
    except Exception as e:
        return jsonify({"error": str(e), "content": ""}), 500

@app.route('/api/clipboard', methods=['POST'])
def set_clipboard():
    try:
        content = request.json.get('content', '')
        # wl-copy sets the clipboard
        subprocess.run(['wl-copy', content], check=True)
        return jsonify({"status": "copied"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Battery Endpoint ---

@app.route('/api/battery', methods=['GET'])
def get_battery():
    # Scan /sys/class/power_supply for BAT*
    bat_path = None
    base = '/sys/class/power_supply'
    if os.path.exists(base):
        for name in os.listdir(base):
            if name.startswith('BAT'):
                bat_path = os.path.join(base, name)
                break
    
    if not bat_path:
         # Fallback mock if no battery found (e.g. desktop)
        return jsonify({
            "percentage": 100,
            "status": "AC Power",
            "is_charging": False
        })
        
    try:
        with open(os.path.join(bat_path, 'capacity'), 'r') as f:
            capacity = int(f.read().strip())
        with open(os.path.join(bat_path, 'status'), 'r') as f:
            status = f.read().strip()
            
        return jsonify({
            "percentage": capacity,
            "status": status,
            "is_charging": status.lower() == 'charging'
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Media Control Endpoints ---

def get_media_player():
    """Finds the first available MPRIS player on DBus."""
    bus = SessionBus()
    try:
        # List names on the bus
        dbus_proxy = bus.get("org.freedesktop.DBus", "/org/freedesktop/DBus")
        names = dbus_proxy.ListNames()
        for name in names:
            if name.startswith("org.mpris.MediaPlayer2"):
                return bus.get(name, "/org/mpris/MediaPlayer2")
    except Exception:
        pass
    return None

@app.route('/api/media', methods=['GET'])
def get_media_status():
    player = get_media_player()
    if not player:
        return jsonify({"status": "No player found"})
        
    try:
        # Standard MPRIS properties
        metadata = player.Metadata
        playback_status = player.PlaybackStatus
        
        # Extract useful info
        # Metadata is a dictionary (variant)
        title = metadata.get('xesam:title', 'Unknown')
        artist = metadata.get('xesam:artist', ['Unknown'])[0] if isinstance(metadata.get('xesam:artist'), list) else 'Unknown'
        
        return jsonify({
            "status": playback_status,
            "title": title,
            "artist": artist
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/media/control', methods=['POST'])
def control_media():
    action = request.json.get('action') # play_pause, previous, next
    player = get_media_player()
    if not player:
        return jsonify({"error": "No player found"}), 404
        
    try:
        if action == 'play_pause':
            player.PlayPause()
        elif action == 'previous':
            player.Previous()
        elif action == 'next':
            player.Next()
        return jsonify({"status": "success", "action": action})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Start the DBus monitor thread
    monitor_thread = threading.Thread(target=monitor_dbus_notifications, daemon=True)
    monitor_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

