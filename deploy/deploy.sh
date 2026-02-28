#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────
#  Bingo Bingo — EC2 One-Click Deploy Script
#  Usage:  sudo bash deploy.sh <your-domain.com>
# ─────────────────────────────────────────────────

if [ $# -lt 1 ]; then
  echo "Usage: sudo bash deploy.sh <your-domain.com>"
  exit 1
fi

DOMAIN="$1"
APP_DIR="/home/ubuntu/bingo_bingo"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
DEPLOY_DIR="$APP_DIR/deploy"

echo "========================================"
echo "  Deploying Bingo Bingo to: $DOMAIN"
echo "========================================"

# ── 1. System packages ──────────────────────────
echo "[1/7] Installing system packages..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

if ! command -v node &> /dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt install -y nodejs
fi

# ── 2. Backend setup ────────────────────────────
echo "[2/7] Setting up backend..."
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
deactivate

if [ ! -f ".env" ]; then
  cp "$DEPLOY_DIR/.env.backend.example" .env
  sed -i "s|yourdomain\.com|$DOMAIN|g" .env
  echo "  → Created backend/.env with CORS origins for $DOMAIN"
fi

# ── 3. Systemd service ─────────────────────────
echo "[3/7] Installing systemd service..."
sed "s|{{DOMAIN}}|$DOMAIN|g" "$DEPLOY_DIR/bingo-backend.service" \
  > /etc/systemd/system/bingo-backend.service

systemctl daemon-reload
systemctl enable bingo-backend
systemctl restart bingo-backend
echo "  → Backend service started on port 8000"

# ── 4. Frontend build ──────────────────────────
echo "[4/7] Building frontend..."
cd "$FRONTEND_DIR"
npm install

echo "VITE_API_BASE_URL=https://$DOMAIN" > .env.production
npm run build
echo "  → Frontend built to dist/"

# ── 5. Nginx config ────────────────────────────
echo "[5/7] Configuring Nginx..."
sed "s|{{DOMAIN}}|$DOMAIN|g; s|{{FRONTEND_DIST}}|$FRONTEND_DIR/dist|g" \
  "$DEPLOY_DIR/nginx-bingo.conf" \
  > /etc/nginx/sites-available/bingo

ln -sf /etc/nginx/sites-available/bingo /etc/nginx/sites-enabled/bingo
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx
echo "  → Nginx configured for $DOMAIN"

# ── 6. HTTPS (Let's Encrypt) ───────────────────
echo "[6/7] Setting up HTTPS..."
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email || {
  echo "  ⚠ Certbot failed. Make sure DNS is pointing to this server."
  echo "  You can retry later with:"
  echo "    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
}

# ── 7. Final check ─────────────────────────────
echo "[7/7] Verifying..."
systemctl status bingo-backend --no-pager || true
echo ""
echo "========================================"
echo "  Deployment complete!"
echo "  https://$DOMAIN"
echo "========================================"
