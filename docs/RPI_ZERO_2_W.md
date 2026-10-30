# Raspberry Pi Zero 2 W — 64-bit deployment

This is a lightweight, demo-only profile for Raspberry Pi Zero 2 W (512 MB RAM).
It uses **SQLite** on a persistent Docker volume and one Gunicorn worker. **Do not use
real accounting/client data without a security review and backups.**

## Prerequisites

- Raspberry Pi OS Lite 64-bit (check `uname -m` returns `aarch64`)
- Docker Engine and the Docker Compose plugin
- Reliable storage and stable power
- Registry access to the published `linux/arm64` image

## Install without cloning git

Create a directory and download only the RPi Compose file and sample environment:

```sh
mkdir -p ~/mdocs && cd ~/mdocs
curl -fsSLo compose.rpi.yaml https://raw.githubusercontent.com/lpioro/mdocs/v0.2.0/compose.rpi.yaml
curl -fsSLo .env.example https://raw.githubusercontent.com/lpioro/mdocs/v0.2.0/.env.example
cp .env.example .env
nano .env
```

Generate a unique long `SECRET_KEY`, e.g. with `python3 -c "import secrets; print(secrets.token_hex(32))"`.
Set the secret in `.env`. `DB_PASSWORD` is unused by this standalone SQLite deployment.

```sh
docker compose -f compose.rpi.yaml pull
docker compose -f compose.rpi.yaml up -d
docker compose -f compose.rpi.yaml exec web flask init-db
docker compose -f compose.rpi.yaml exec -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD='CHOOSE_A_LONG_UNIQUE_PASSWORD' web flask create-admin
docker compose -f compose.rpi.yaml ps
docker compose -f compose.rpi.yaml logs --tail=100 web
```

The service binds only to `127.0.0.1:8000` on the Pi. Access through an authenticated HTTPS reverse proxy or a correctly configured Cloudflare Tunnel, not direct port forwarding. If accessing via HTTPS, set `COOKIE_SECURE=1` in `.env` and restart.

## Data, backup and updates

The SQLite database lives in Docker named volume `sqlite_data`. Back up the SQLite database using SQLite's online backup API while the service is running, or stop the service and copy the volume content (including any SQLite journal files).

Example consistent backup using the running Python container:

```sh
mkdir -p ~/mdocs/backups
docker compose -f compose.rpi.yaml exec -T web python -c "import sqlite3; src=sqlite3.connect('/data/monitor.db'); dst=sqlite3.connect('/data/backup.db'); src.backup(dst); dst.close(); src.close()"
docker cp "$(docker compose -f compose.rpi.yaml ps -q web):/data/backup.db" ~/mdocs/backups/monitor-backup.db
```

Backup files contain sensitive data: encrypt and retain them outside the Raspberry Pi.

To update, choose a tested image tag in `.env` via `APP_IMAGE`, back up the data, then:

```sh
docker compose -f compose.rpi.yaml pull
docker compose -f compose.rpi.yaml up -d
```

Application `flask init-db` creates missing tables; it is **not** a schema migration mechanism. Test database changes before upgrades.

## Caveats

- No OCR, LLM, IMAP integration or actual sending of reminders yet.
- SQLite is intended for light single-instance use; it is not a substitute for PostgreSQL for a growing installation.
- The container depends on successful publication of `ghcr.io/lpioro/mdocs:v0.2.0` with `linux/arm64` support.
