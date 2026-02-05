# KDE Connect Webapp - Tailscale Isolation Project

## Overview

This project implements a secure, multi-tenant capable **KDE Connect Web Application** that runs isolated instances within Linux Network Namespaces. Each instance is exposed to the internet via **Tailscale Funnel**, allowing users to connect their devices (phones/tablets) to a private, ephemeral server instance without exposing the host network or other instances.

The core goal is to provide a "cloud-like" experience for KDE Connect, where a user can spin up a server, pair their device, and interact with it (send notifications, commands, etc.) securely over Tailscale.

## Architecture

The system is composed of three main layers:

1.  **Orchestrator (Flask App)**: Manages lifecycle of isolated environments.
2.  **Isolation Layer (Namespaces)**: Provides network isolation for each session.
3.  **Service Layer (KDE Connect & Tailscale)**: The actual application running inside the isolation.

### Architectural Diagram

```mermaid
graph TD
    User[User Browser]
    Phone[User Phone (Tailscale)]
    
    subgraph Host [Host Machine]
        Flask[Orchestrator App (app.py)]
        ProcessMgr[IsolationManager]
        
        subgraph NS [Network Namespace (ns-uuid)]
            Tailscaled[tailscaled (userspace)]
            KDE[kdeconnect-webapp-d]
            Veth[veth-interface]
        end
    end

    User -->|HTTP| Flask
    Flask -->|Manage| ProcessMgr
    ProcessMgr -->|Create/Destroy| NS
    
    Phone -->|Tailscale Funnel| Tailscaled
    Tailscaled -->|Localhost| KDE
```

## Key Components

### 1. Orchestrator (`tailscale_integrated/app.py`)
A Flask web application that serves as the control panel.
- **Login**: Simulates authentication (currently generates a UUID session).
- **Session Management**: Tracks active instances linked to user sessions.
- **UI**: Displays status, QR codes for pairing, and public Funnel URLs.
- **Cleanup**: Handles stopping instances and removing namespaces.

### 2. Isolation Manager (`tailscale_integrated/isolation_manager.py`)
The heavy lifter responsible for system-level operations.
- **Auth Keys**: Interacts with Tailscale API to generate ephemeral, tagged auth keys for new instances.
- **Namespace Setup**: 
    - Creates a new Linux Network Namespace (`ip netns`).
    - Creates veth pairs to connect the namespace to the host.
    - Configures NAT (Masquerading) via `iptables` to allow internet access from within the namespace.
    - Sets up DNS (`/etc/netns/...`).
- **Service Launch**:
    - Starts `tailscaled` in userspace mode inside the namespace.
    - Starts `kdeconnect-webapp-d` (the Python web server) inside the namespace.
- **Funneling**: Configures Tailscale Funnel to publicly expose the internal service port.

### 3. KDE Connect Webapp (`kdeconnect_webapp/`)
The core application logic, based on the KDE Connect protocol.
- **Server (`server.py`)**: Twisted-based async server. Listen's for device packets and API requests.
- **API (`api.py`)**: REST API to interact with connected devices (Ping, Ring, Notifications, Commands).
- **Protocol**: Handles the encryption and identity exchange required by KDE Connect.

## Setup & Installation

### Prerequisites
- **Linux**: Requires a kernel supporting network namespaces (`ip netns`).
- **Python 3.8+**
- **Tailscale**:
    - `tailscale` and `tailscaled` installed on the host.
    - A Tailscale account with API keys.
    - Funnel enabled on your Tailnet.
- **Root Privileges**: Required for manipulating network namespaces and iptables.

### Configuration
Create a `.env` file in the `tailscale_integrated/` directory:

```bash
CLIENT_ID=ts_client_...       # Tailscale OAuth Client ID
CLIENT_SECRET=ts_secret_...   # Tailscale OAuth Client Secret
TAILNET=example.tailnet.ts.net # Your Tailnet name
```

### Dependencies
Install Python dependencies:

```bash
# In virtualization environment (venv) ideally
pip install -r requirements.txt
pip install -e . # Install the kdeconnect-webapp package in editable mode
```

Note: You may need `flask`, `requests`, `qrcode`, `Pillow` (PIL).

### Running the Orchestrator
Because of network namespace operations, the app must likely be run as root (or with capabilities `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`).

```bash
sudo python3 tailscale_integrated/app.py
```

Access the dashboard at `http://localhost:5000`.

## workflow Description

1.  **Initialization**: User clicks "Start Isolated Service".
2.  **Auth Key Generation**: System requests a key with tag `tag:kcadmin` from Tailscale.
3.  **Isolation**:
    - Create `ns-<id>`.
    - Setup `veth` pair.
    - Enable NAT outbound.
4.  **Service Start**:
    - `kdeconnect-webapp-d` starts on port 8081 (default).
    - `tailscaled` starts, using `/tmp/tailscale-<id>.sock` and state dir.
5.  **Tunneling**: System runs `tailscale funnel` to expose port 8081.
6.  **Ready**: User gets a public URL (e.g., `https://ns-1234.tailnet.ts.net`) and a QR code to authorize.

## Troubleshooting

- **Namespace Persistence**: If the app crashes, namespaces (`ip netns list`) and veth interfaces may remain. Use `sudo ip netns delete <name>` to clean up.
- **Funnel Errors**: Ensure HTTPS certificates are provisioned (takes time) and that your ACLs allow Funnel.
- **Permission Denied**: Almost always because `sudo` was forgotten.
- **Tailscale Socket**: Each instance uses a unique socket in `/tmp/`. Ensure `/tmp` is writable.

## Directory Structure

- `kdeconnect_webapp/`: Core library code.
- `tailscale_integrated/`: The isolation and orchestrator logic.
    - `app.py`: Web UI.
    - `isolation_manager.py`: System automation.
- `tailscaleterm/` & `client-isolated-env/`: Experimental/Test folders.
- `frontend/`: Svelte/Web frontend assets (if applicable).
