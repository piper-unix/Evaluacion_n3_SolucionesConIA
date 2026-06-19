#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-https://github.com/TU-USUARIO/agente-metro-santiago.git}"
APP_DIR="$HOME/app"

echo ">> [1/4] Instalando Docker…"
if ! command -v docker >/dev/null 2>&1; then
  sudo dnf install -y docker
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER"
  echo "   ✅ Docker instalado. Necesitarás logout/login para usar docker sin sudo."
else
  echo "   ✅ Docker ya instalado"
fi

echo ">> [2/4] Instalando plugin docker compose…"
if ! docker compose version >/dev/null 2>&1; then
  sudo mkdir -p /usr/local/lib/docker/cli-plugins
  ARCH="$(uname -m)"
  sudo curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-${ARCH}" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
  echo "   ✅ Docker Compose instalado"
else
  echo "   ✅ Docker Compose ya instalado"
fi

echo ">> [3/4] Clonando repositorio…"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
  echo "   ✅ Repositorio clonado"
else
  git -C "$APP_DIR" pull --ff-only
  echo "   ✅ Repositorio actualizado"
fi

echo ">> [4/4] Verificando firewall…"
if command -v firewall-cmd >/dev/null 2>&1; then
  sudo firewall-cmd --permanent --add-port=80/tcp 2>/dev/null || true
  sudo firewall-cmd --permanent --add-port=443/tcp 2>/dev/null || true
  sudo firewall-cmd --reload 2>/dev/null || true
  echo "   ✅ Puertos 80/443 abiertos en firewall"
else
  echo "   ⚠️  No se detectó firewalld — asegúrate de que el Security Group de AWS tenga puertos 80 y 443 abiertos"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            ✅  BOOTSTRAP COMPLETADO  ✅                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Próximos pasos:"
echo ""
echo "  1. cd $APP_DIR"
echo "  2. cp .env.example .env"
echo "  3. nano .env          # pegar OPENAI_API_KEY=sk-..."
echo ""
echo "  4. docker compose -f deploy/docker-compose.prod.yml build"
echo "  5. docker compose -f deploy/docker-compose.prod.yml up -d"
echo ""
echo "  6. Abrir en el navegador: http://$(curl -s http://checkip.amazonaws.com || echo '<IP_PUBLICA>')"
echo ""
echo "Seguridad aplicada:"
echo "  - Contenedores con usuario no-root"
echo "  - Red interna (solo Caddy expone puertos)"
echo "  - Rate limiting (Caddy + FastAPI)"
echo "  - Detección de prompt injection"
echo "  - Filtros de datos sensibles (RUT, tarjetas, etc.)"
echo "  - HTTPS con cabeceras de seguridad"
echo "  - OWASP LLM Top 10 mitigado"
echo ""
