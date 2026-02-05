#!/usr/bin/env python3
"""
Tailscale API - Remove all tags from a device by its Tailscale IP

Requirements:
    pip install requests
"""

import requests
import json
import sys
from typing import Optional
from dotenv import load_dotenv
import os

# ────────────────────────────────────────────────
#  CONFIGURATION - FILL THESE IN
# ────────────────────────────────────────────────

load_dotenv()
TAILSCALE_API_KEY = os.getenv("TAILSCALE_API_KEY")
TAILNET = os.getenv("TAILNET")



BASE_URL = f"https://api.tailscale.com/api/v2/tailnet/{TAILNET}"


def get_device_by_ip(tailscale_ip: str) -> Optional[dict]:
    """
    Find device by its Tailscale IP (e.g. 100.x.y.z)
    Returns the full device object or None
    """
    url = f"{BASE_URL}/devices"
    headers = {
        "Authorization": f"Bearer {TAILSCALE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        data = r.json()

        for device in data.get("devices", []):
            if tailscale_ip in device.get("addresses", []):
                return device

        print(f"No device found with IP {tailscale_ip}", file=sys.stderr)
        return None

    except requests.RequestException as e:
        print(f"Error fetching devices: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            try:
                print("Response:", e.response.text[:400], file=sys.stderr)
            except:
                pass
        return None


def remove_all_tags(device_id: str) -> bool:
    """
    Remove all tags from a device.
    Endpoint: POST /api/v2/device/{device-id}/tags
    (Note: Tailscale uses POST to set tags, not PATCH)
    """
    url = f"https://api.tailscale.com/api/v2/device/{device_id}/tags"
    headers = {
        "Authorization": f"Bearer {TAILSCALE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "tags": []          # empty list = remove all tags
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        r.raise_for_status()

        updated = r.json()
        print("Success! Tags removed.")
        print("Updated device info:")
        print(json.dumps(updated, indent=2))
        return True

    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        if e.response is not None:
            try:
                err = e.response.json()
                print("API message:", err.get("message", "No message"), file=sys.stderr)
                print("Status code:", e.response.status_code, file=sys.stderr)
            except:
                print("Raw response:", e.response.text[:500], file=sys.stderr)
        return False

    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python remove-tags.py 100.x.y.z")
        print("Example:")
        print("  python remove-tags.py 100.123.124.6")
        sys.exit(1)

    ip = sys.argv[1].strip()

    if not ip.startswith("100."):
        print("Warning: Tailscale IPs usually start with 100.", file=sys.stderr)

    print(f"Looking for device with IP: {ip}")

    device = get_device_by_ip(ip)
    if not device:
        print("Device not found.", file=sys.stderr)
        sys.exit(2)

    device_id = device.get("id")
    if not device_id:
        print("Error: Device response missing 'id' field", file=sys.stderr)
        print("Full device:", json.dumps(device, indent=2), file=sys.stderr)
        sys.exit(3)

    hostname = device.get("name", "unknown")
    current_tags = device.get("tags", [])

    print(f"Found device: {hostname}")
    print(f"  Device ID   : {device_id}")
    print(f"  Current tags: {current_tags or '<none>'}")

    if not current_tags:
        print("Device already has no tags. Nothing to do.")
        sys.exit(0)

    print("\nRemoving all tags...")

    success = remove_all_tags(device_id)
    if not success:
        sys.exit(4)


if __name__ == "__main__":
    main()
