{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.wireguard-tools
    (pkgs.python3.withPackages (ps: with ps; [
      flask
      segno
    ]))
  ];

  shellHook = ''
    echo "WireGuard Python Environment Loaded"
    echo "Python version: $(python --version)"
    echo "WireGuard tools: $(wg --version)"
  '';
}
