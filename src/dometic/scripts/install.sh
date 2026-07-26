#!/usr/bin/env bash
# Install the daemon into /opt/dometic and enable the systemd service.
# Run on a Raspberry Pi as root (or with sudo).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="/opt/dometic"

if [[ $EUID -ne 0 ]]; then
    echo "Please run as root: sudo $0"
    exit 1
fi

echo "==> Installing system dependencies"
apt-get update
apt-get install -y --no-install-recommends \
    python3-venv python3-pip python3-dev \
    i2c-tools

echo "==> Creating $INSTALL_DIR"
mkdir -p "$INSTALL_DIR" "$INSTALL_DIR/config"

echo "==> Copying source"
rsync -a --delete \
    --exclude='.git' --exclude='.venv' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='.env' --exclude='config/config.yaml' \
    "$REPO_DIR/" "$INSTALL_DIR/"

echo "==> Creating venv"
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --upgrade pip wheel
"$INSTALL_DIR/.venv/bin/pip" install -e "$INSTALL_DIR"

if [[ ! -f "$INSTALL_DIR/config/config.yaml" ]]; then
    echo "==> Copying example config"
    cp "$INSTALL_DIR/config/config.example.yaml" "$INSTALL_DIR/config/config.yaml"
fi

echo "==> Installing systemd service"
cp "$INSTALL_DIR/systemd/dometic.service" /etc/systemd/system/dometic.service
systemctl daemon-reload
systemctl enable dometic.service
systemctl restart dometic.service

echo
echo "==> Done. Status:"
systemctl status dometic.service --no-pager
