{ pkgs ? import <nixpkgs> {} }:

let
  # Define the specific python environment with required packages
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    flask
    requests
    qrcode
    pillow
    python-dotenv
  ]);
in
pkgs.mkShell {
  name = "tailscale-server-env";

  # nativeBuildInputs contains tools you'll use in the shell
  nativeBuildInputs = with pkgs; [
    pythonEnv
    tailscale    # Includes tailscale and tailscaled
    curl         # For testing the web server
    netcat       # For testing UDP if needed
  ];

  shellHook = ''
    echo "--- Tailscale Python Server Environment ---"
    echo "Python version: $(python --version)"
    echo "Tailscale version: $(tailscale version | head -n 1)"
    echo "Ready. Run 'python server.py' to start."
    echo "-------------------------------------------"
  '';
}
