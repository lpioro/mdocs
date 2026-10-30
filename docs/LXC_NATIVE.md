# Native deployment on Proxmox LXC (without Docker)

This guide is for the **current `lpioro/mdocs` application** (Flask app factory in `app/`, `wsgi.py`). It is **not** an installer for the recovered legacy `/root/monitor-docs/app.py` unless that code is migrated into this repository first.

## Target

- Debian 12/13 or Ubuntu LXC, running systemd, with internet access and Python 3 venv support
- App code: `/opt/mdocs`
- Unix account: `mdocs`
- SQLite data: `/var/lib/mdocs/monitor.db` (persistent across git updates)
- Configuration/secrets: `/etc/mdocs/mdocs.env` (never commit to Git)
- Local service: Gunicorn on `127.0.0.1:8000`
- Service name: `mdocs.service`

Proxmox LXC is a system container. Installing Python inside it **does not require Docker or Kubernetes**.

## Install

Run **inside the target LXC as root**:

```bash
apt-get update && apt-get install -y git
git clone https://github.com/lpioro/mdocs.git /opt/mdocs
cd /opt/mdocs
bash deploy/lxc/install.sh
```

Script creates a service account, installs Python dependencies into `.venv`, generates `SECRET_KEY` once, initializes empty SQLite tables (does not wipe an existing database), and starts systemd. Verify:

```bash
systemctl status mdocs --no-pager
journalctl -u mdocs -n 50 --no-pager
curl -i http://127.0.0.1:8000/health
```

### First administrator

Use an interactive prompt instead of placing the password in shell history:

```bash
runuser -u mdocs -- bash -c '
  set -a; source /etc/mdocs/mdocs.env; set +a
  cd /opt/mdocs
  export ADMIN_USERNAME=admin
  read -rsp "Admin password (12+ chars): " ADMIN_PASSWORD; echo
  export ADMIN_PASSWORD
  .venv/bin/flask --app wsgi:app create-admin
'
```

If admin already exists, the command will refuse to create a duplicate.

## Cloudflare / reverse proxy

Configure `cloudflared` on **the same LXC** with an ingress entry targeting `http://127.0.0.1:8000`, or proxy from Nginx to that address. Example ingress entry (place before the final 404 rule):

```yaml
- hostname: docs.example.com
  service: http://127.0.0.1:8000
```

The public hostname also needs a DNS route pointing at the selected tunnel. Do not change an existing tunnel/hostname without checking its current owner and routes. If HTTPS is used externally, change `COOKIE_SECURE=1` in `/etc/mdocs/mdocs.env` and run `systemctl restart mdocs`.

To access the service directly from LAN for a quick test, use a reverse proxy rather than opening Gunicorn to all interfaces. Do not expose the built-in Flask debug server.

## Upgrade

Back up the database first (see below). Then, from inside the LXC:

```bash
cd /opt/mdocs
git pull --ff-only
bash deploy/lxc/install.sh
```

The installer keeps existing environment secrets and SQLite files. It reruns `flask init-db` to create missing tables; **it does not perform schema migrations**. Test any database changes before upgrading production. For reproducibility, pin a reviewed Git tag or commit rather than blindly tracking `main`.

## Backup / restore

A safe online SQLite backup (rather than copying a live file) can be made with:

```bash
install -d -m 0700 /root/mdocs-backups
python3 - <<'PY'
import sqlite3
src = sqlite3.connect('file:/var/lib/mdocs/monitor.db?mode=ro', uri=True)
dst = sqlite3.connect('/root/mdocs-backups/monitor.db')
with dst:
    src.backup(dst)
dst.close()
src.close()
PY
```

Protect and encrypt backups if they contain client data. Backup `/etc/mdocs/mdocs.env` separately and securely; never upload it to a public repository. Stop `mdocs` before replacing/restoring the live database and ensure `mdocs:mdocs` ownership.

## Troubleshooting

```bash
systemctl status mdocs --no-pager
journalctl -u mdocs -e --no-pager
ss -lntp | grep 8000
curl -i http://127.0.0.1:8000/health
```

Check tunnel configuration and DNS separately when local HTTP responds but the domain fails.

## Constraints

This repo is an MVP, not a production-ready accounting/document processing system. It lacks real IMAP ingestion, OCR/AI processing, schema migrations, and a full security review. Avoid real client data until security, privacy and backup requirements have been evaluated.
