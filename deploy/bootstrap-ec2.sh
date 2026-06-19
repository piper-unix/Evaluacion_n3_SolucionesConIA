#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-https://github.com/TU-USUARIO/agente-metro-santiago.git}"
APP_DIR="$HOME/app"

echo ">> Instalando Docker…"
if ! command -v docker >/dev/null 2>&1; then
  sudo dnf install -y docker
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER" || true
fi

echo ">> Instalando plugin docker compose…"
if ! docker compose version >/dev/null 2>&1; then
  sudo mkdir -p /usr/local/lib/docker/cli-plugins
  ARCH="$(uname -m)"
  sudo curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-${ARCH}" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

echo ">> Clonando repo…"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only
fi

echo ">> Listo. Siguiente:"
echo "   cd $APP_DIR"
echo "   cp .env.example .env && nano .env"
echo "   docker compose -f deploy/docker-compose.prod.yml up --build -d"
