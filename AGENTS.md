# Repository Guidelines

## Project Structure & Module Organization
- `kdeconnect_webapp/` is the core Python package (server, client, protocol, API, packet handling).
- `kdeconnect_webapp/webapp/` contains static assets served by the app (HTML/CSS/JS).
- `frontend/webapp-old/` is a legacy UI snapshot.
- `docs/` holds diagrams and documentation artifacts.
- `client-isolated-env/`, `python-vpn/`, and `tailscaletest/` are auxiliary experiments/tools; treat them as separate from the main package.
- `kdeconnect-webapp.service` is a systemd unit example.

## Build, Test, and Development Commands
- `nix-shell` enters the development environment.
- `source env/bin/activate` activates the Python environment (from the `env/` folder).
- `kdeconnect-webapp-d --name MyFakeDevice --discovery-port 1717` starts the server in dev.
- `kdeconnect-webapp --help` and `kdeconnect-webapp-d --help` show CLI/server options.
- `isort --diff kdeconnect_webapp/*.py` checks import ordering.
- `flake8 kdeconnect_webapp/*.py` runs lint checks.
- `pytest -vv` runs tests (pytest is configured to look in `tests/`).
- `python -m build --wheel` builds a wheel; `twine check dist/*` validates artifacts.

## Coding Style & Naming Conventions
- Follow PEP 8 conventions (4-space indentation, snake_case for modules/functions, CapWords for classes).
- Keep imports sorted via `isort` and lint with `flake8` before submitting.
- Prefer small, focused modules inside `kdeconnect_webapp/` and keep CLI entrypoints in `client.py`/`server.py`.

## Testing Guidelines
- The project uses `pytest`; discovery is configured for a `tests/` directory.
- Name tests `test_*.py` and functions `test_*`.
- Add focused tests for new behavior and note how to run them.

## Commit & Pull Request Guidelines
- Recent commits use short, imperative messages (e.g., “moved frontend to new folder”). Keep messages concise and descriptive.
- PRs should include: a brief summary, a list of key changes, and testing notes (commands run or “not run”).
- Include screenshots for any UI changes in `kdeconnect_webapp/webapp/` or `frontend/`.

## Configuration & Security Notes
- Service configuration is demonstrated in `kdeconnect-webapp.service`; update `User` and `WorkingDirectory` before use.
- Avoid committing secrets or private keys (there are test keys under `client-isolated-env/test/` for local use only).
