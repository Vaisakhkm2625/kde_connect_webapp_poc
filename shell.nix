{ pkgs ? import <nixpkgs> {} }:

let
  # Define a single Python environment with packages for both projects
  pythonEnv = pkgs.python313.withPackages (ps: with ps; [
    # kdeconnect-webapp dependencies
    pillow
    pyopenssl
    requests
    twisted
    paramiko

    # tailscale_integrated / Flask app dependencies
    flask
    qrcode
    python-dotenv

    # nice-to-haves for development & debugging
    black
    ruff
    pytest
    ipython
  ]);

in
pkgs.mkShell {
  name = "kdeconnect-webapp-and-tailscale-dev";

  # Tools and runtimes available in the shell
  nativeBuildInputs = with pkgs; [
    pythonEnv

    # Tailscale support
    tailscale
    #tailscaled   # optional - if you want to run tailscaled in the shell

    # Useful utilities
    curl
    netcat-openbsd   # nc - for port checking
    git
    just             # optional: nice task runner (alternative to make)
  ];

  # Optional: environment variables you might find useful
  # TAILSCALE_LOGIN_SERVER = "https://controlplane.tailscale.com";  # example

  shellHook = ''
    echo
    echo "══════════════════════════════════════════════════════════════"
    echo "  kdeconnect-webapp + tailscale_integrated development shell"
    echo "══════════════════════════════════════════════════════════════"
    echo
    echo "Python:        $(python --version)"
    echo "pip packages:  flask, twisted, pillow, pyopenssl, requests, qrcode, python-dotenv"
    echo "Tailscale:     $(tailscale version | head -n 1 || echo 'not found')"
    echo
    echo "Available commands:"
    echo "  python tailscale_integrated/app.py          → run Flask app"
    echo "  kdeconnect-webapp-d                         → run kdeconnect daemon"
    echo "  kdeconnect-webapp                           → run kdeconnect client"
    echo "  tailscale up --accept-routes                → connect tailscale (if needed)"
    echo "  tailscale status                            → check tailscale status"
    echo
    echo "Tip: You usually don't need sudo to run these."
    echo "══════════════════════════════════════════════════════════════"
    echo
  '';
}
