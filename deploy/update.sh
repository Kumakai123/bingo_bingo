#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────
#  Bingo Bingo — Quick Update Script
#  Run after `git pull` to rebuild and restart.
#  Usage:  sudo bash deploy/update.sh
# ─────────────────────────────────────────────────

APP_DIR="/home/ubuntu/bingo_bingo"

echo "── Updating backend..."
cd "$APP_DIR/backend"
source venv/bin/activate
pip install -r requirements.txt --quiet
deactivate
sudo systemctl restart bingo-backend

echo "── Rebuilding frontend..."
cd "$APP_DIR/frontend"
npm install --silent
npm run build
chmod -R 755 /home/ubuntu/bingo_bingo/frontend/dist 2>/dev/null || true

echo "── Reloading Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo "── Done! Services restarted."
