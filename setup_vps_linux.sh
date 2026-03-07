#!/bin/bash
set -euo pipefail

# ============================================
# Setup PokéMMO Bot en Linux VPS (headless)
# Requiere: Ubuntu 22.04+ / Debian 12+
# ============================================

echo "=== PokéMMO Bot - Setup VPS Linux ==="

# 1. Dependencias del sistema
echo "[1/6] Instalando dependencias del sistema..."
sudo apt update
sudo apt install -y \
    xvfb \
    x11vnc \
    fluxbox \
    openjdk-17-jre \
    python3 python3-pip python3-venv \
    wget unzip \
    mesa-utils \
    libgl1-mesa-dri \
    libegl1-mesa \
    xdotool \
    scrot \
    git

# 2. Display virtual
echo "[2/6] Configurando display virtual (Xvfb)..."
# Mata instancias previas
pkill Xvfb 2>/dev/null || true
sleep 1

# Crear display 1920x1080 (mismo que las refs)
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
echo "export DISPLAY=:99" >> ~/.bashrc

# Window manager minimo
fluxbox &

echo "[2/6] Display :99 activo (1920x1080x24)"

# 3. VNC para monitorizar (opcional)
echo "[3/6] Iniciando VNC server (puerto 5900)..."
x11vnc -display :99 -forever -nopw -bg -quiet
echo "[3/6] VNC activo. Conecta con cualquier cliente VNC a <tu-ip>:5900"

# 4. PokéMMO
echo "[4/6] Descargando PokéMMO..."
POKEMMO_DIR="$HOME/pokemmo-client"
if [ ! -d "$POKEMMO_DIR" ]; then
    mkdir -p "$POKEMMO_DIR"
    cd "$POKEMMO_DIR"
    wget -q "https://pokemmo.com/download" -O pokemmo.zip 2>/dev/null || {
        echo "  Descarga manual: https://pokemmo.com/download"
        echo "  Descomprime en $POKEMMO_DIR"
    }
    # Si se descargo, descomprimir
    [ -f pokemmo.zip ] && unzip -q pokemmo.zip && rm pokemmo.zip
    cd -
else
    echo "  PokéMMO ya instalado en $POKEMMO_DIR"
fi

# 5. Bot
echo "[5/6] Configurando bot..."
BOT_DIR="$HOME/pokemmo-bot"
if [ ! -d "$BOT_DIR" ]; then
    git clone https://github.com/pedrodnc/pokemmo-bot.git "$BOT_DIR"
fi
cd "$BOT_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt

# 6. Scripts de arranque
echo "[6/6] Creando scripts de arranque..."

cat > "$HOME/start_pokemmo.sh" << 'SCRIPT'
#!/bin/bash
export DISPLAY=:99
# Verificar que Xvfb esta corriendo
if ! pgrep -x Xvfb > /dev/null; then
    Xvfb :99 -screen 0 1920x1080x24 &
    sleep 1
    fluxbox &
    x11vnc -display :99 -forever -nopw -bg -quiet
fi
cd ~/pokemmo-client
java -jar pokemmo-client.jar &
echo "PokéMMO iniciado. Conecta VNC a $(hostname -I | awk '{print $1}'):5900"
SCRIPT
chmod +x "$HOME/start_pokemmo.sh"

cat > "$HOME/start_bot.sh" << 'SCRIPT'
#!/bin/bash
export DISPLAY=:99
cd ~/pokemmo-bot
source .venv/bin/activate
python src/main.py
SCRIPT
chmod +x "$HOME/start_bot.sh"

echo ""
echo "=== Setup completado ==="
echo ""
echo "Pasos siguientes:"
echo "  1. ~/start_pokemmo.sh     → Arranca PokéMMO"
echo "  2. Conecta VNC a $(hostname -I 2>/dev/null | awk '{print $1}'):5900"
echo "  3. Configura PokéMMO: login, resolucion 1920x1080, keybinds (Z=A, X=B)"
echo "  4. Posicionate en el Centro Pokemon"
echo "  5. ~/start_bot.sh         → Arranca el bot"
echo ""
echo "Para modo agente IA:"
echo "  export ANTHROPIC_API_KEY=sk-ant-..."
echo "  Edita config.toml: [bot] MODE = \"agent\", [ai] ENABLED = true"
