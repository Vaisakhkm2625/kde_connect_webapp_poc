{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "kdeconnect-webapp-dev";

  buildInputs = with pkgs; [
    # Python environment with the exact packages we need


    python313
    python313Packages.pip
    nodejs_22
    pnpm

    tailscale    # Includes tailscale and tailscaled
    curl         # For testing the web server
    netcat       # For testing UDP if needed

    (python313.withPackages (ps: with ps; [
      pillow
      pyopenssl
      requests
      twisted

      # Optional — very useful during development
      black
      ruff          # fast linter + formatter
      pytest
      ipython


    flask
    qrcode
    python-dotenv

    ]))

    # Some general utilities you might want
    git
    just          # optional: nice alternative to make
  ];

  shellHook = ''
    echo
    echo "kdeconnect-webapp development shell"
    echo "Python: $(python --version)"
    echo "pip list | grep -E 'pillow|twisted|pyopenssl|requests'"
    echo
    echo "Available commands:"
    echo "  kdeconnect-webapp     → run the client"
    echo "  kdeconnect-webapp-d   → run the daemon/server"
    echo
  '';
}
