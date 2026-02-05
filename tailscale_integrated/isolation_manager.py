import os
import sys
import time
import subprocess
import requests
import logging
from pathlib import Path
import uuid
import re

# Configuration defaults (can be overridden)
SERVER_PORT = 8081
NS_IPV4 = "192.168.200.2/24"
HOST_IPV4 = "192.168.200.1/24"
# Interfaces will be dynamically named based on namespace to avoid collisions

class IsolationManager:
    def __init__(self, client_id, client_secret, tailnet):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tailnet = tailnet
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("tailscale_integrated.log", mode='a')
            ]
        )

    def get_auth_key(self, tags=None):
        """Fetches an OAuth token and creates a tagged ephemeral Auth Key."""
        if tags is None:
            tags = ["tag:kcadmin","tag:kcuser1"] # Default tag

        token_url = "https://login.tailscale.com/api/v2/oauth/token"
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        token_resp = requests.post(token_url, data=token_data)
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        key_url = f"https://api.tailscale.com/api/v2/tailnet/{self.tailnet}/keys"
        payload = {
            "capabilities": {
                "devices": {
                    "create": {
                        "reusable": True,
                        "ephemeral": False,
                        "tags": tags
                    }
                }
            },
            "expirySeconds": 3600   # 1 hour
        }
        # headers = {"Authorization": f"Bearer {access_token}"}
        key_resp = requests.post(key_url, json=payload, auth=(access_token, ''))
        key_resp.raise_for_status()

        key_data = key_resp.json()
        auth_key = key_data.get("key")
        if not auth_key:
            raise RuntimeError("Failed to get auth key from response")

        logging.info(f"Generated auth key (ephemeral, tagged {tags}): {auth_key[:12]}...")
        return auth_key

    def _get_default_interface(self):
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

    def setup_namespace(self, ns_name):
        """Create namespace + veth pair + NAT + default route (with cleanup)"""
        logging.info(f"Setting up namespace {ns_name} with internet access...")

        # Make interface names unique per namespace to avoid collisions
        # Limit to 15 chars (standard linux interface name limit)
        # veth-h-123456
        veth_host = f"veth-h-{ns_name[:6]}"
        veth_ns   = f"veth-n-{ns_name[:6]}"

        main_interface = self._get_default_interface()
        if not main_interface:
            raise RuntimeError("Could not detect default network interface")

        logging.info(f"Detected main interface: {main_interface}")

        # Cleanup any leftover interfaces
        for iface in [veth_host, veth_ns]:
            subprocess.run(["ip", "link", "delete", iface], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Cleanup namespace if it exists
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
             
            ## Allow forwarding (Insert at top to avoid being blocked by default DROP/REJECT)
            #["iptables", "-I", "FORWARD", "1", "-i", veth_host, "-j", "ACCEPT"],
            #["iptables", "-I", "FORWARD", "1", "-o", veth_host, "-j", "ACCEPT"],

            # Default route inside namespace
            ["ip", "netns", "exec", ns_name, "ip", "route", "add", "default", "via", "192.168.200.1"],
        ]

        # # Setup DNS for the namespace
        # # By creating /etc/netns/<name>/resolv.conf, ip netns exec will bind mount it over /etc/resolv.conf
        # try:
        #     netns_conf_dir = f"/etc/netns/{ns_name}"
        #     os.makedirs(netns_conf_dir, exist_ok=True)
        #     with open(f"{netns_conf_dir}/resolv.conf", "w") as f:
        #         f.write("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
        # except Exception as e:
        #     logging.error(f"Failed to setup DNS: {e}")
        #     raise

        for cmd in cmds:
            logging.info(f"Running: {' '.join(cmd)}")
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                logging.error(f"Command failed: {' '.join(cmd)}\nStdout: {e.stdout}\nStderr: {e.stderr}")
                raise

    def start_kdeconnect(self, ns_name, port=SERVER_PORT):
        """Runs kdeconnect-webapp-d inside the namespace"""
        logging.info(f"Starting kdeconnect-webapp-d in namespace {ns_name} on admin port {port}")

        # We assume kdeconnect-webapp-d is in the PATH as requested.
        # --name MyFakeDevice --discovery-port 1717 --admin-port 8081
        
        # cmd = [
        #     "ip", "netns", "exec", ns_name,
        #     "kdeconnect-webapp-d",
        #     "--name", "MyFakeDevice", 
        #     "--discovery-port", "1717",
        #     "--admin-port", str(port)
        # ]

        # cmd = [
        #     "ip", "netns", "exec", ns_name,
        #     "python3",
        #     "-m", "http.server", 
        #     "8080"
        # ]
        #

        cmd = [
            "ip", "netns", "exec", ns_name,
            "python","-m", "kdeconnect_webapp.server",
            "--name", "MyFakeDevice", 
            "--discovery-port", "1717",
            "--admin-port", str(port)
        ]

        proc = subprocess.Popen(cmd)
        return proc

    def join_tailscale(self, ns_name, auth_key):
        """Runs tailscaled + tailscale up inside the namespace"""
        logging.info(f"Joining {ns_name} to tailnet...")

        state_dir = f"/var/lib/tailscale/{ns_name}"
        socket_path = f"/tmp/tailscale-{ns_name}.sock"
        
        # Ensure state dir exists is handled by tailscaled usually, but creating parent path is good
        Path(state_dir).mkdir(parents=True, exist_ok=True)

        tailscaled_proc = subprocess.Popen([
            "ip", "netns", "exec", ns_name,
            "tailscaled",
            "--tun=userspace-networking",
            f"--state={state_dir}/tailscaled.state",
            f"--socket={socket_path}",
            # "--verbose=1"
        ])

        # Give tailscaled time to initialize
        time.sleep(4)

        up_cmd = [
            "ip", "netns", "exec", ns_name,
            "tailscale",
            "--socket", socket_path,
            "up",
            f"--authkey={auth_key}",
            "--accept-routes",
            "--accept-dns=false",
            f"--hostname={ns_name}",
        ]
        
        up_result = subprocess.run(up_cmd, capture_output=True, text=True)

        logging.info("tailscale up output:")
        logging.info(up_result.stdout)
        if up_result.returncode != 0:
            logging.error("tailscale up failed:")
            logging.error(up_result.stderr)
            raise RuntimeError("Failed to join tailnet")

        logging.info(f"Namespace {ns_name} joined to tailnet!")
        return tailscaled_proc

    def enable_funnel(self, ns_name):
        socket_path = f"/tmp/tailscale-{ns_name}.sock"
        
        # Generate random UUID for hostname part to attempt to get a unique one if needed
        # But tailscale usually handles hostnames. 
        # The script used `enable_funnel_with_uuid` which did some guessing.
        
        logging.info(f"Requesting public URL funnel for {ns_name}")

        funnel_cmd = [
            "ip", "netns", "exec", ns_name,
            "tailscale", "--socket", socket_path,
            "funnel",
            "--bg",
            str(SERVER_PORT)
        ]

        result = subprocess.run(funnel_cmd, capture_output=True, text=True)
        logging.info("Funnel output:")
        logging.info(result.stdout)
        logging.info(result.stderr)

        if result.returncode != 0:
            logging.error("Funnel failed:")
            logging.error(result.stderr)
            raise RuntimeError("Failed to enable Funnel")

        # Extract URL
        match = re.search(r'(https://[^\s]+)', result.stdout)
        if match:
            return match.group(1)
        
        # If not found in stdout, it might be that it's already running or output different.
        # We can try `tailscale funnel status` or just guess based on previous behavior
        # But for now, let's try to fetch status
        status_cmd = [
             "ip", "netns", "exec", ns_name,
             "tailscale", "--socket", socket_path,
             "funnel", "status", "--json"
        ]
        # This might be too complex for now, let's fallback to constructing it if we can
        # or just waiting a bit.
        
        # Fallback simplistic guess
        return f"https://{ns_name}.{self.tailnet}.ts.net"

    def cleanup(self, ns_name):
        """Cleanup namespace and related interfaces/rules"""
        logging.info(f"Cleaning up namespace {ns_name}")
        
        veth_host = f"veth-h-{ns_name[:6]}"
        veth_ns   = f"veth-n-{ns_name[:6]}"

        # Remove NAT rule
        subprocess.run([
            "iptables", "-t", "nat", "-D", "POSTROUTING",
            "-s", "192.168.200.0/24", "-j", "MASQUERADE"
        ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Remove FORWARD rules
        subprocess.run(["iptables", "-D", "FORWARD", "-i", veth_host, "-j", "ACCEPT"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["iptables", "-D", "FORWARD", "-o", veth_host, "-j", "ACCEPT"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Remove DNS config
        import shutil
        try:
            shutil.rmtree(f"/etc/netns/{ns_name}", ignore_errors=True)
        except Exception as e:
            logging.error(f"Failed to remove DNS config: {e}")

        # Remove veth interfaces
        for iface in [veth_host, veth_ns]:
            subprocess.run(["ip", "link", "delete", iface], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Delete namespace
        subprocess.run(["ip", "netns", "delete", ns_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
