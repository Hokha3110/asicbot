#!/bin/bash
# ====================================================================
# Ubuntu 22.04 LTS Installation & Setup Script for Security Solution Copilot Backend
# ====================================================================

set -e

echo "=== [1/6] Updating Ubuntu packages & Installing Dependencies ==="
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential libpq-dev git curl nginx

echo "=== [2/6] Setting up PostgreSQL Database (Optional / Recommended) ==="
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql

sudo -u postgres psql -c "CREATE USER presales_admin WITH PASSWORD 'SecurePassword_2026!';" || true
sudo -u postgres psql -c "CREATE DATABASE security_copilot OWNER presales_admin;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE security_copilot TO presales_admin;" || true

echo "=== [3/6] Setting up Python Virtual Environment ==="
cd /opt/security-copilot/backend || cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== [4/6] Creating Environment Variables ==="
if [ ! -f .env ]; then
    cp ../.env.example .env
    echo "Created .env from .env.example. Please update your API Keys in .env"
fi

echo "=== [5/6] Configuring Systemd Service ==="
sudo cp systemd/security-copilot-be.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable security-copilot-be
sudo systemctl restart security-copilot-be

echo "=== [6/6] Backend Status Check ==="
sudo systemctl status security-copilot-be --no-pager

echo "===================================================================="
echo "Backend deployed successfully on Ubuntu 22.04 LTS!"
echo "API Docs available at: http://<YOUR_UBUNTU_IP>:8000/docs"
echo "Healthcheck: http://<YOUR_UBUNTU_IP>:8000/api/health"
echo "===================================================================="
