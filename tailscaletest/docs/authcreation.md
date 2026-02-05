

Implementation Steps

OAuth: Go to the Tailscale Settings and create a new OAuth Client. Give it Devices: Generate Auth Keys permission and ensure you select the tag:user-device in the tags section.

https://login.tailscale.com/admin/settings/trust-credentials

-  Environment: Run nix-shell in your directory.

- Run: Execute python app.py.

- Onboarding: Navigate to http://localhost:5000. Scan the QR code with your Android phone's Tailscale app.

- Access: Once the phone is connected, find its IP in the Tailscale app, enter it into the web form, and click "Fetch."

- Would you like me to help you write a simple Python-based UDP server that you can run on Android via Termux to test the communication?
