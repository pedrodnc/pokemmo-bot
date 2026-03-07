# Ejecutar el bot en VPS

## Opcion 1: Windows VPS (recomendado)

La forma mas simple. PokéMMO + bot corren nativamente.

### Setup

1. Alquila un Windows VPS (Hetzner, OVH, Contabo — desde ~10€/mes)
2. Conecta por RDP
3. Instala:
   - Java 17+ (para PokéMMO)
   - Python 3.10+ (para el bot)
   - PokéMMO
4. Clona el bot:
   ```cmd
   git clone https://github.com/pedrodnc/pokemmo-bot.git
   cd pokemmo-bot
   pip install -r requirements.txt
   ```
5. Configura `config.toml` (ajustar WINDOW_TITLE si es necesario)
6. Abre PokéMMO, posicionate en el Centro Pokemon
7. Ejecuta el bot:
   ```cmd
   python src/main.py
   ```
8. Desconecta del RDP — el bot sigue corriendo

### Nota importante
Al desconectar RDP, Windows minimiza las ventanas. El bot necesita foco.
Solucion: usa TightVNC en vez de RDP, o configura el VPS para no bloquear la sesion:
```cmd
tscon %sessionname% /dest:console
```

## Opcion 2: Modo agente IA (experimental)

Usa Claude API para analizar screenshots y tomar decisiones autonomamente.
Mas flexible que scripts, funciona incluso si las refs no coinciden.

### Setup

1. Instala el SDK de Anthropic:
   ```cmd
   pip install anthropic
   ```

2. Configura tu API key:
   ```cmd
   set ANTHROPIC_API_KEY=sk-ant-...
   ```

3. Edita `config.toml`:
   ```toml
   [bot]
   MODE = "agent"

   [ai]
   ENABLED = true
   MODEL = "claude-haiku-4-5-20251001"
   CHECK_INTERVAL = 10
   AI_HP_CHECK = true
   ```

4. Ejecuta:
   ```cmd
   python src/main.py
   ```

### Costes estimados

| Modelo | Coste/llamada | Check cada 10s | Coste/hora | Coste/dia |
|---|---|---|---|---|
| Haiku 4.5 | ~$0.001 | 360 calls/h | ~$0.36 | ~$8.64 |
| Haiku 4.5 | ~$0.001 | Check cada 30s | ~$0.12 | ~$2.88 |
| Sonnet 4.6 | ~$0.01 | 360 calls/h | ~$3.60 | ~$86.40 |

**Recomendacion**: Haiku 4.5 con CHECK_INTERVAL = 30 (~$3/dia).

### Modo hibrido (recomendado para VPS)

La mejor relacion coste/eficacia: pixel matching para reacciones rapidas (batalla) + IA para decisiones estrategicas (curar, estado del juego).

```toml
[bot]
MODE = "script"

[ai]
ENABLED = true
CHECK_INTERVAL = 30
AI_HP_CHECK = true
```

El bot usa scripts normales pero la IA analiza el HP cada 30s y recomienda curar cuando es necesario. Coste: ~$3/dia.

## Opcion 3: Linux VPS con display virtual

Para VPS Linux baratos (sin GUI).

### Setup

```bash
# Instalar dependencias
sudo apt install xvfb x11vnc fluxbox openjdk-17-jre python3-pip

# Crear display virtual
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Window manager minimo
fluxbox &

# VNC para monitorizar (opcional)
x11vnc -display :99 -forever -nopw &

# Instalar PokéMMO
# (descargar desde pokemmo.com, descomprimir, ejecutar)
java -jar pokemmo-client.jar &

# Instalar y ejecutar bot
git clone https://github.com/pedrodnc/pokemmo-bot.git
cd pokemmo-bot
pip3 install -r requirements.txt
python3 src/main.py
```

### Notas
- PokéMMO usa OpenGL — necesita Mesa/LLVMpipe para software rendering
- Rendimiento grafico bajo sin GPU, pero funciona
- Conectar via VNC para configurar el juego inicialmente
- pyautogui funciona con Xvfb sin problemas
