#!/usr/bin/env python3
"""
Creates an isolated network namespace with:
- veth pair + NAT for real internet access
- simple HTTP server
- tailscaled in userspace-networking mode
- joins Tailscale using ephemeral tagged auth key

Requires: root privileges, tailscale installed, requests library, iptables
"""

import os
import sys
import time
import subprocess
import requests
import argparse
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ────────────────────────────────────────────────
#  Configuration - from environment
# ────────────────────────────────────────────────

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TAILNET = os.getenv("TAILNET")          # example: example.com

if not all([CLIENT_ID, CLIENT_SECRET, TAILNET]):
    print("Missing required environment variables:")
    print("  CLIENT_ID, CLIENT_SECRET, TAILNET")
    sys.exit(1)

SERVER_PORT = 8080                      # port the HTTP server listens on
TAG = "tag:kcuser1"                     # ← change to your tag

# Networking config inside namespace
NS_IPV4 = "192.168.200.2/24"
HOST_IPV4 = "192.168.200.1/24"
VETH_NS = "veth-ns"                     # interface name inside namespace
VETH_HOST = "veth-host"                 # interface name on host

# ────────────────────────────────────────────────
#  Tailscale Auth Key generation
# ────────────────────────────────────────────────

def get_auth_key():
    """Fetches an OAuth token and creates a tagged ephemeral Auth Key."""
    token_url = "https://login.tailscale.com/api/v2/oauth/token"
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    token_resp = requests.post(token_url, data=token_data)
    token_resp.raise_for_status()
    access_token = token_resp.json()["access_token"]

    key_url = f"https://api.tailscale.com/api/v2/tailnet/{TAILNET}/keys"
    payload = {
        "capabilities": {
            "devices": {
                "create": {
                    "reusable": False,
                    "ephemeral": True,
                    "tags": [TAG]
                }
            }
        },
        "expirySeconds": 3600   # 1 hour
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    key_resp = requests.post(key_url, json=payload, headers=headers)
    key_resp.raise_for_status()

    key_data = key_resp.json()
    auth_key = key_data.get("key")
    if not auth_key:
        raise RuntimeError("Failed to get auth key from response")

    print(f"Generated auth key (ephemeral, tagged {TAG}): {auth_key[:12]}...")
    return auth_key

# ────────────────────────────────────────────────
#  Namespace + Networking Setup
# ────────────────────────────────────────────────

# def setup_namespace_with_internet(ns_name: str):
#     """Create namespace + veth pair + NAT + default route"""
#     print(f"Setting up namespace {ns_name} with internet access...")
#
#     main_interface = get_default_interface()
#     if not main_interface:
#         raise RuntimeError("Could not detect default network interface")
#
#     print(f"Detected main interface: {main_interface}")
#
#     cmds = [
#         # Create namespace
#         ["ip", "netns", "add", ns_name],
#
#         # Create veth pair
#         ["ip", "link", "add", VETH_HOST, "type", "veth", "peer", "name", VETH_NS],
#
#         # Move namespace end into namespace
#         ["ip", "link", "set", VETH_NS, "netns", ns_name],
#
#         # Configure IPs
#         ["ip", "netns", "exec", ns_name, "ip", "addr", "add", NS_IPV4, "dev", VETH_NS],
#         ["ip", "netns", "exec", ns_name, "ip", "link", "set", VETH_NS, "up"],
#         ["ip", "addr", "add", HOST_IPV4, "dev", VETH_HOST],
#         ["ip", "link", "set", VETH_HOST, "up"],
#
#         # Enable loopback inside namespace
#         ["ip", "netns", "exec", ns_name, "ip", "link", "set", "lo", "up"],
#
#         # Enable IP forwarding on host
#         ["sysctl", "-w", "net.ipv4.ip_forward=1"],
#
#         # Add NAT (masquerade)
#         ["iptables", "-t", "nat", "-A", "POSTROUTING",
#          "-s", "192.168.200.0/24",
#          "-o", main_interface, "-j", "MASQUERADE"],
#
#         # Default route inside namespace
#         ["ip", "netns", "exec", ns_name, "ip", "route", "add", "default", "via", "192.168.200.1"],
#     ]
#
#     for cmd in cmds:
#         print(f"Running: {' '.join(cmd)}")
#         subprocess.run(cmd, check=True)

def setup_namespace_with_internet(ns_name: str):
    """Create namespace + veth pair + NAT + default route (with cleanup)"""
    print(f"Setting up namespace {ns_name} with internet access...")

    # Make interface names unique per namespace
    veth_host = f"veth-h-{ns_name}"
    veth_ns   = f"veth-n-{ns_name}"

    main_interface = get_default_interface()
    if not main_interface:
        raise RuntimeError("Could not detect default network interface")

    print(f"Detected main interface: {main_interface}")

    # Cleanup any leftover interfaces from previous failed runs
    for iface in [veth_host, veth_ns]:
        subprocess.run(["ip", "link", "delete", iface], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Also make sure namespace is gone if it exists
    subprocess.run(["ip", "netns", "delete", ns_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    cmds = [
        # Create namespace
        ["ip", "netns", "add", ns_name],

        # Create veth pair
        ["ip", "link", "add", veth_host, "type", "veth", "peer", "name", veth_ns],

        # Move namespace end into namespace
        ["ip", "link", "set", veth_ns, "netns", ns_name],

        # Configure IPs
        ["ip", "netns", "exec", ns_name, "ip", "addr", "add", NS_IPV4, "dev", veth_ns],
        ["ip", "netns", "exec", ns_name, "ip", "link", "set", veth_ns, "up"],
        ["ip", "addr", "add", HOST_IPV4, "dev", veth_host],
        ["ip", "link", "set", veth_host, "up"],

        # Enable loopback
        ["ip", "netns", "exec", ns_name, "ip", "link", "set", "lo", "up"],

        # Enable IP forwarding
        ["sysctl", "-w", "net.ipv4.ip_forward=1"],

        # Add NAT rule
        ["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-s", "192.168.200.0/24",
         "-o", main_interface, "-j", "MASQUERADE"],

        # Default route inside namespace
        ["ip", "netns", "exec", ns_name, "ip", "route", "add", "default", "via", "192.168.200.1"],
    ]

    for cmd in cmds:
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)



def get_default_interface():
    """Find the interface with default route"""
    try:
        output = subprocess.check_output(["ip", "-4", "route", "show", "default"]).decode()
        for line in output.splitlines():
            if "dev" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "dev":
                        return parts[i + 1]
        return None
    except Exception:
        return None


def start_http_server_in_namespace(ns_name: str, port: int = SERVER_PORT):
    """Runs a very simple HTTP server inside the namespace"""
    print(f"Starting HTTP server in namespace {ns_name} on port {port}")

    server_code = f"""
import http.server
import socketserver
print("Simple HTTP server running on port {port} inside namespace")
with socketserver.TCPServer(("", {port}), http.server.SimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()
"""

    script_path = f"/tmp/simple-server-{ns_name}.py"
    with open(script_path, "w") as f:
        f.write(server_code)

    proc = subprocess.Popen([
        "ip", "netns", "exec", ns_name,
        "python3", script_path
    ])

    return proc, script_path


def join_tailscale_in_namespace(ns_name: str, auth_key: str):
    """Runs tailscaled + tailscale up inside the namespace"""
    print(f"Joining {ns_name} to tailnet...")

    state_dir = f"/var/lib/tailscale/{ns_name}"
    socket_path = f"/tmp/tailscale-{ns_name}.sock"

    Path(state_dir).mkdir(parents=True, exist_ok=True)

    tailscaled_proc = subprocess.Popen([
        "ip", "netns", "exec", ns_name,
        "tailscaled",
        "--tun=userspace-networking",
        f"--state={state_dir}/tailscaled.state",
        f"--socket={socket_path}",
        "--verbose=1"
    ])

    # Give tailscaled time to initialize
    time.sleep(4)

    up_result = subprocess.run([
        "ip", "netns", "exec", ns_name,
        "tailscale",
        "--socket", socket_path,
        "up",
        f"--authkey={auth_key}",
        "--accept-routes",
        "--accept-dns=false",
        f"--hostname={ns_name}",
    ], capture_output=True, text=True)

    print("tailscale up output:")
    print(up_result.stdout)
    if up_result.returncode != 0:
        print("tailscale up failed:")
        print(up_result.stderr)
        raise RuntimeError("Failed to join tailnet")

    print(f"Namespace {ns_name} joined to tailnet!")

    return tailscaled_proc


# def cleanup_namespace(ns_name: str):
#     """Basic cleanup — delete namespace and remove iptables rule"""
#     print(f"Cleaning up namespace {ns_name}")
#
#     # Remove NAT rule
#     subprocess.run([
#         "iptables", "-t", "nat", "-D", "POSTROUTING",
#         "-s", "192.168.200.0/24", "-j", "MASQUERADE"
#     ], check=False)
#
#     # Delete namespace (also stops processes inside)
#     subprocess.run(["ip", "netns", "delete", ns_name], check=False)

def cleanup_namespace(ns_name: str):
    """Cleanup namespace and related interfaces/rules"""
    print(f"Cleaning up namespace {ns_name}")

    veth_host = f"veth-h-{ns_name}"
    veth_ns   = f"veth-n-{ns_name}"

    # Remove NAT rule
    subprocess.run([
        "iptables", "-t", "nat", "-D", "POSTROUTING",
        "-s", "192.168.200.0/24", "-j", "MASQUERADE"
    ], check=False)

    # Remove veth interfaces
    for iface in [veth_host, veth_ns]:
        subprocess.run(["ip", "link", "delete", iface], check=False)

    # Delete namespace
    subprocess.run(["ip", "netns", "delete", ns_name], check=False)

def enable_funnel_with_uuid(ns_name: str, socket_path: str):
    import uuid

    # Generate random UUID subdomain
    random_uuid = uuid.uuid4().hex[:12]          # e.g. "a1b2c3d4e5f6"
    hostname = f"{random_uuid}.{TAILNET}"        # your-tailnet.ts.net
    full_domain = f"{random_uuid}.{TAILNET}.ts.net"

    print(f"Requesting public URL: https://{full_domain}")

    # Run tailscale funnel command inside the namespace
    funnel_cmd = [
        "ip", "netns", "exec", ns_name,
        "tailscale", "--socket", socket_path,
        "funnel",
        "--bg",
        # "--hostname", hostname,
        str(SERVER_PORT)
    ]

    result = subprocess.run(funnel_cmd, capture_output=True, text=True)

    print("Funnel output:")
    print(result.stdout)

    if result.returncode != 0:
        print("Funnel failed:")
        print(result.stderr)
        raise RuntimeError("Failed to enable Funnel")

    print("\n" + "═"*70)
    print(f"Public URL (randomized):  https://{full_domain}")
    print("This URL is now publicly accessible on the internet")
    print("═"*70 + "\n")

    return full_domain

# ────────────────────────────────────────────────
#  Main logic
# ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="ns-test", help="Name of the namespace")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup after demo")
    args = parser.parse_args()

    ns_name = args.name

    server_proc = None
    tailscaled_proc = None

    try:
        # 1. Generate auth key
        auth_key = get_auth_key()

        # 2. Setup namespace + networking + internet
        setup_namespace_with_internet(ns_name)

        # 3. Start HTTP server
        server_proc, _ = start_http_server_in_namespace(ns_name)

        # 4. Join Tailscale
        tailscaled_proc = join_tailscale_in_namespace(ns_name, auth_key)


        public_url = enable_funnel_with_uuid(ns_name, f"/tmp/tailscale-{ns_name}.sock")

        print("\n" + "="*70)
        print(f"Success! Namespace '{ns_name}' is running")
        print(f"→ HTTP server running inside on port {SERVER_PORT}")
        print(f"→ Find Tailscale IP:")
        print(f"  sudo ip netns exec {ns_name} tailscale ip -4")
        print("Press Ctrl+C to stop...\n")

        print(f" public url -> {public_url}")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if server_proc:
            server_proc.terminate()
        if tailscaled_proc:
            tailscaled_proc.terminate()

        if args.cleanup:
            cleanup_namespace(ns_name)
        else:
            print("\nNamespace still exists. Cleanup manually if needed:")
            print(f"  sudo ip netns delete {ns_name}")
            print("  sudo iptables -t nat -D POSTROUTING -s 192.168.200.0/24 -j MASQUERADE")


if __name__ == "__main__":
    main()
