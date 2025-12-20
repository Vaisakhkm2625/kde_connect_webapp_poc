{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    python313
    python313Packages.pip
    #python3Packages.virtualenv
  ];

  buildInputs = with pkgs.python313Packages; [
    pillow
    pyopenssl
    requests
    twisted
  ];

# # Optional development dependencies
# shellHook = ''
#   # Create a virtualenv if it doesn't exist
#   if [ ! -d .venv ]; then
#     ${python3Packages.virtualenv}/bin/virtualenv .venv
#   fi
#   source .venv/bin/activate
#
#   # Upgrade pip and install optional devel tools
#   pip install --upgrade pip
#   pip install build flake8 isort pytest twine
#
#   echo "konnect environment ready! Run 'konnect' or 'konnectd' after installing the package."
#   echo "To install the package locally: pip install -e ."
# '';
}
