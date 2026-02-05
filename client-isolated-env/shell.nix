{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    # Python with the required libraries
    (pkgs.python313.withPackages (python-pkgs: with python-pkgs; [
      cryptography
      twisted
      qrcode
      requests
      # Optional: pillow is usually required by qrcode to generate image files
      pillow 
    ]))

    # System tools for WireGuard management and debugging
    pkgs.wireguard-tools
  ];

  shellHook = ''
    echo "--- WireGuard Python Development Environment ---"
    echo "Python version: $(python --version)"
    echo "Available tools: wg, wg-quick"
    echo "------------------------------------------------"
  '';
}
