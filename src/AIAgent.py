"""
AIAgent — Agente de IA para PokéMMO bot.

Usa Claude API (vision) para analizar screenshots del juego y tomar decisiones.
Diseñado para funcionar en VPS con display virtual (Xvfb/VNC) o Windows RDP.

Modos de uso:
  1. Asistente: analiza HP, estado del juego, etc. para ayudar al script
  2. Autonomo: toma todas las decisiones sin script (experimental)

Requiere:
  - ANTHROPIC_API_KEY en variable de entorno
  - pip install anthropic Pillow
"""

import json
import time
import io
import base64

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import pyautogui as pag
    from PIL import Image
    HAS_SCREENSHOT = True
except ImportError:
    HAS_SCREENSHOT = False


SYSTEM_PROMPT = """Eres un asistente de analisis visual para un bot de PokéMMO.
Analizas screenshots del juego y devuelves SOLO un JSON con el estado del juego.

El juego es PokéMMO, un MMO de Pokemon. Las pantallas posibles son:
- overworld: el jugador esta en el mapa caminando
- battle: pantalla de combate contra un Pokemon salvaje o trainer
- center: dentro del Centro Pokemon (edificio con mostrador/enfermera)
- dialog: cuadro de dialogo abierto (texto en la parte inferior)
- menu: menu del juego abierto (inventario, equipo, etc.)
- black: pantalla negra (transicion, carga, whiteout)
- unknown: no puedes determinar

Para HP, mira la barra de vida del Pokemon del jugador:
- Verde = 50-100%, Amarillo = 25-50%, Rojo = 0-25%
- Si no ves barra de HP, pon null

Responde SOLO con JSON valido, sin markdown ni texto extra."""

ANALYSIS_PROMPT = """Analiza este screenshot de PokéMMO. Responde SOLO con JSON:
{
  "state": "overworld|battle|center|dialog|menu|black|unknown",
  "hp_percent": <numero 0-100 o null si no visible>,
  "in_grass": <true/false o null>,
  "needs_heal": <true/false>,
  "battle_won": <true/false o null>,
  "error": <null o descripcion del problema>
}"""


class AIAgent:
    """Agente IA que analiza screenshots del juego via Claude API."""

    def __init__(self, model="claude-haiku-4-5-20251001", check_interval=10):
        if not HAS_ANTHROPIC:
            raise ImportError("pip install anthropic")
        if not HAS_SCREENSHOT:
            raise ImportError("pip install pyautogui Pillow")

        self.client = anthropic.Anthropic()
        self.model = model
        self.check_interval = check_interval
        self.last_check = 0
        self.last_state = None
        self.call_count = 0

    def capture_screenshot(self, region=None, scale=0.5):
        """Captura screenshot y la escala para reducir tokens."""
        screenshot = pag.screenshot(region=region)
        if scale != 1.0:
            new_size = (int(screenshot.width * scale), int(screenshot.height * scale))
            screenshot = screenshot.resize(new_size, Image.LANCZOS)

        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG', optimize=True)
        return base64.b64encode(buffer.getvalue()).decode()

    def analyze(self, force=False):
        """Analiza el estado actual del juego via screenshot + IA.

        Returns:
            dict con state, hp_percent, in_grass, needs_heal, etc.
            None si no toca analizar todavia (check_interval)
        """
        now = time.time()
        if not force and (now - self.last_check) < self.check_interval:
            return self.last_state

        try:
            img_b64 = self.capture_screenshot(scale=0.5)
            self.call_count += 1

            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_b64,
                            }
                        },
                        {"type": "text", "text": ANALYSIS_PROMPT}
                    ]
                }]
            )

            text = response.content[0].text.strip()
            # Limpiar markdown si la IA lo mete
            if text.startswith('```'):
                text = text.split('\n', 1)[1].rsplit('```', 1)[0]
            state = json.loads(text)
            self.last_state = state
            self.last_check = now
            return state

        except json.JSONDecodeError as e:
            print(f'[AI] Error parseando respuesta: {e}')
            return self.last_state
        except Exception as e:
            print(f'[AI] Error: {e}')
            return self.last_state

    def needs_heal(self):
        """Pregunta a la IA si necesitamos curar."""
        state = self.analyze()
        if state and state.get('needs_heal'):
            return True
        if state and state.get('hp_percent') is not None:
            return state['hp_percent'] < 30
        return False

    def get_state(self):
        """Devuelve el estado actual del juego."""
        return self.analyze() or {"state": "unknown"}

    def get_stats(self):
        """Devuelve estadisticas de uso."""
        return {
            "calls": self.call_count,
            "last_state": self.last_state,
        }


class AIAutonomousAgent:
    """Agente autonomo que juega PokéMMO sin scripts.

    Toma decisiones basadas en el estado visual del juego.
    Experimental — mas lento que scripts pero mas flexible.
    """

    def __init__(self, action, ai_agent, battle_handler):
        self.action = action
        self.ai = ai_agent
        self.battle = battle_handler
        self.running = False
        self.battles_since_heal = 0
        self.max_battles = 5

    def run(self):
        """Loop principal del agente autonomo."""
        self.running = True
        print('[AI-AGENT] Modo autonomo iniciado')

        while self.running:
            state = self.ai.analyze(force=True)
            if not state:
                time.sleep(1)
                continue

            game_state = state.get('state', 'unknown')
            print(f'[AI-AGENT] Estado: {game_state} | HP: {state.get("hp_percent")} | Batallas: {self.battles_since_heal}')

            if game_state == 'battle':
                self._handle_battle()
            elif game_state == 'center':
                self._handle_center()
            elif game_state == 'dialog':
                self._handle_dialog()
            elif game_state == 'overworld':
                self._handle_overworld(state)
            elif game_state == 'black':
                time.sleep(2)
            else:
                time.sleep(1)

    def stop(self):
        self.running = False

    def _handle_battle(self):
        """Maneja una batalla."""
        self.battle.do_battle(
            wait_fn=self.action.waitFor,
            timeout=120
        )
        self.battles_since_heal += 1
        time.sleep(1)

    def _handle_center(self):
        """Cura en el centro Pokemon."""
        # Hablar con la enfermera (spam Z por el dialogo)
        for _ in range(6):
            self.action.pressKey('z')
            time.sleep(1)
        self.battles_since_heal = 0
        # Salir del centro
        self.action.holdKey('down' if hasattr(self.action, 'holdKey') else None)
        time.sleep(1.5)
        self.action.releaseKey('down')
        time.sleep(0.5)

    def _handle_dialog(self):
        """Cierra dialogos."""
        self.action.pressKey('z')
        time.sleep(0.5)

    def _handle_overworld(self, state):
        """Decide que hacer en el mapa."""
        needs_heal = state.get('needs_heal', False)
        hp = state.get('hp_percent')

        if needs_heal or (hp is not None and hp < 30) or self.battles_since_heal >= self.max_battles:
            print('[AI-AGENT] Necesito curar, buscando centro...')
            # Caminar hacia arriba buscando el centro
            self.action.holdKey('up')
            self.action.waitFor('center', timeout=30)
            time.sleep(0.5)
            self.action.releaseKey('up')
        else:
            # Caminar en hierba para provocar encuentro
            direction = ['up', 'right', 'down', 'left'][self.battles_since_heal % 4]
            from pynput.keyboard import Key
            key_map = {'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right}
            self.action.holdKey(key_map[direction])
            time.sleep(1.5)
            self.action.releaseKey(key_map[direction])
            time.sleep(0.3)
