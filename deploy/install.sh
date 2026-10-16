#!/usr/bin/env bash
# Instala o actualiza el asistente en el Wyse (Debian 12). Ejecutar como root:
#   primera vez: sudo git clone <repo> /opt/asistente && sudo bash /opt/asistente/deploy/install.sh
#   actualizar:  sudo bash /opt/asistente/deploy/install.sh
set -euo pipefail

REPO="${1:-}"
DESTINO=/opt/asistente

apt-get update
apt-get install -y --no-install-recommends python3 python3-venv python3-pip git ca-certificates

id asistente &>/dev/null || useradd --system --home "$DESTINO" --shell /usr/sbin/nologin asistente

# El repo pertenece al usuario 'asistente' pero lo actualiza root
git config --global --add safe.directory "$DESTINO"

if [ ! -d "$DESTINO/.git" ]; then
    [ -n "$REPO" ] || { echo "Uso: $0 <url-del-repo>"; exit 1; }
    git clone "$REPO" "$DESTINO"
else
    git -C "$DESTINO" pull --ff-only
fi

mkdir -p "$DESTINO/data" "$DESTINO/conocimiento"
python3 -m venv "$DESTINO/.venv"
"$DESTINO/.venv/bin/pip" install --upgrade pip
"$DESTINO/.venv/bin/pip" install -r "$DESTINO/requirements.txt"

[ -f "$DESTINO/.env" ] || cp "$DESTINO/.env.example" "$DESTINO/.env"
[ -f "$DESTINO/config/cuentas.yaml" ] || cp "$DESTINO/config/cuentas.example.yaml" "$DESTINO/config/cuentas.yaml"
chown -R asistente:asistente "$DESTINO"
chmod 600 "$DESTINO/.env" "$DESTINO/config/cuentas.yaml"

cp "$DESTINO/deploy/asistente.service" /etc/systemd/system/asistente.service
systemctl daemon-reload
systemctl enable asistente
systemctl restart asistente
echo "Listo. Logs: journalctl -u asistente -f"
