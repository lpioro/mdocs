#!/usr/bin/env bash
# Native deployment for Debian/Ubuntu LXC. Run as root inside the container.
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run as root inside the LXC container." >&2
  exit 1
fi
if [[ ! -f "./wsgi.py" || ! -f "./requirements.txt" || ! -d "./app" ]]; then
  echo "Run this script from the root directory of the mdocs repository." >&2
  exit 1
fi
if [[ "$(realpath .)" != "/opt/mdocs" ]]; then
  echo "Clone the repository to /opt/mdocs and run: cd /opt/mdocs && bash deploy/lxc/install.sh" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv python3-pip git ca-certificates

if ! id -u mdocs >/dev/null 2>&1; then
  useradd --system --home-dir /var/lib/mdocs --shell /usr/sbin/nologin --user-group mdocs
fi
install -d -o mdocs -g mdocs -m 0750 /var/lib/mdocs
install -d -o root -g mdocs -m 0750 /etc/mdocs

if [[ ! -f /etc/mdocs/mdocs.env ]]; then
  secret="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  cat > /etc/mdocs/mdocs.env <<EOF
APP_ENV=production
SECRET_KEY=${secret}
DATABASE_URL=sqlite:////var/lib/mdocs/monitor.db
COOKIE_SECURE=0
EOF
  chown root:mdocs /etc/mdocs/mdocs.env
  chmod 0640 /etc/mdocs/mdocs.env
  echo "Created /etc/mdocs/mdocs.env. Set COOKIE_SECURE=1 when served via HTTPS."
else
  echo "Keeping existing /etc/mdocs/mdocs.env (secrets and DB settings preserved)."
fi

python3 -m venv /opt/mdocs/.venv
/opt/mdocs/.venv/bin/python -m pip install --upgrade pip
/opt/mdocs/.venv/bin/python -m pip install -r /opt/mdocs/requirements.txt

install -o root -g root -m 0644 deploy/lxc/mdocs.service /etc/systemd/system/mdocs.service
systemctl daemon-reload

# Create tables only; this does not migrate existing schemas.
runuser -u mdocs -- /bin/bash -c '
  set -a
  source /etc/mdocs/mdocs.env
  set +a
  cd /opt/mdocs
  .venv/bin/flask --app wsgi:app init-db
'

systemctl enable --now mdocs
systemctl restart mdocs
systemctl --no-pager --full status mdocs || true
echo
echo "Local health check:"
curl -fsS http://127.0.0.1:8000/health || true
echo
echo "Next: create administrator using the instructions in docs/LXC_NATIVE.md"
