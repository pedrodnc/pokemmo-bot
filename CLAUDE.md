# CLAUDE.md - PokéMMO Bot

## Qué es esto

Bot de farming automático para PokéMMO (cliente MMO basado en Pokémon Gen 3-5).
Fork de [caamillo/alphaForny](https://github.com/caamillo/alphaForny) con mejoras inspiradas en [RedTrainer](https://github.com/yzsvdu/RedTrainer) pero sin inyección — 100% externo (image recognition + input simulation).

## Arquitectura

```
src/
  main.py            → Entrada. Carga config, selecciona script, arranca AlphaForny
  AlphaForny.py      → Clase principal. Gestiona threads (ejecución + input listener)
  FornyTranslator.py → Parsea scripts .txt, traduce comandos a acciones, maneja batalla
  Action.py          → Ejecuta acciones: teclado, ratón, image recognition, auto-focus
  BattleHandler.py   → Logica de batalla: seleccion de movimiento, auto-catch
  Config.py          → Lee config.toml
  Translator.py      → Clase Translator: acceso a strings i18n con notación dot
  Script.py          → Navegador de scripts en menú interactivo
  Language.py        → i18n (en.json / it.json)

scripts/
  Exp/
    Route3_Striaton.txt    → Farm early Unova (Striaton City → Route 3) ← ACTIVO
    Route2_EarlyUnova.txt  → Farm early Unova (Accumula Town → Route 2)
    Spiraria.txt           → Farm mid-late (requiere HM Surf)
  Fish/
    BasicFish.txt          → Pesca basica (requiere refs/excl.png)
  Gym/Unima/               → Gym rematch (vacíos, sin implementar)
  Custom/
    AntiAFK.txt            → Anti-AFK (camina en cuadrado)

refs/                      → Imágenes de referencia para image recognition (1920x1080)
```

## Cómo funciona

### DSL de scripts

Los scripts .txt tienen dos secciones: `setup:` (se ejecuta una vez) y `loop:` (bucle infinito).

Comandos:
```
PRESS <key>           → Pulsa y suelta una tecla
HOLD <key>            → Mantiene pulsada una tecla
RELEASE <key>         → Suelta una tecla
SLEEP <segundos>      → Espera N segundos (con jitter aleatorio ±20%)
WAITFOR <ref>         → Espera hasta detectar refs/<ref>.png en pantalla (timeout 120s)
UNTIL <ref>           → Espera hasta que refs/<ref>.png DEJE de aparecer
SPAM <key>            → Empieza a spamear una tecla en background thread
STOPSPAM <key>        → Para el spam
CLICK <x>,<y>         → Click de ratón en coordenadas absolutas
PRINT <texto>         → Log en consola
WALK <patron>         → Movimiento con patron configurable (zigzag/circle/random/leftright/updown)
FISH <tecla_cana>     → Ciclo de pesca: lanzar cana → esperar picada → enganchar → pelear
```

Teclas especiales: UP, DOWN, LEFT, RIGHT, SHIFT. El resto son caracteres literales (z, x, j...).

### Detección de batalla mid-walk

Durante cualquier `SLEEP >= 0.5s` o `WALK`, el bot checkea cada 0.5s si aparece la pantalla de batalla (`lotta.png`). Si la detecta:
1. Suelta todas las teclas de movimiento
2. Ejecuta la batalla (selección de movimiento configurable + spam para diálogos)
3. Marca `battle_handled = True` → salta los WAITFOR/SPAM/STOPSPAM del script
4. Continúa con la vuelta al centro

### BattleHandler

Maneja la lógica de batalla basándose en config.toml:
- `MOVE_SLOT`: qué movimiento usar (1-4, layout 2x2 del menú de batalla)
- `AUTO_CATCH`: si true, intenta lanzar Pokeball antes de pelear

### Auto-focus (Windows)

El bot trae la ventana de PokéMMO al frente automáticamente al arrancar y antes de cada acción importante. Configurable con `AUTO_FOCUS` en config.toml.

## Config (config.toml)

```toml
[battle]
MOVE_SLOT = 1          # Slot del movimiento (1-4)
AUTO_CATCH = false     # Intentar capturar

[walk]
PATTERN = "zigzag"     # zigzag, circle, random, leftright, updown
STEP_DURATION = 1.5    # Segundos por paso
STEPS = 6              # Pasos por ciclo

[safety]
WAITFOR_TIMEOUT = 120  # Timeout WAITFOR en segundos
SLEEP_JITTER = 0.2     # Variación aleatoria ±20%
AUTO_FOCUS = true      # Traer ventana al frente
```

## Setup en Windows

```bat
pip install -r requirements.txt
python src/main.py
```

Requisitos: Python 3.10+, resolución 1920x1080, PokéMMO en ventana.

## Features vs RedTrainer

| Feature | RedTrainer (inyección) | Este bot (externo) |
|---|---|---|
| Selección de movimiento | Reflection directa | Config MOVE_SLOT (1-4) |
| Auto-catch | Reflection directa | Image recognition + nav menú |
| Walk patterns | Circle/Random/LR/UD | WALK command (mismos patrones) |
| Auto-fish | Reflection directa | FISH command + refs/excl.png |
| Sin foco (background) | Java Reflection | NO — necesita foco (auto-focus) |
| Detección HP | Lee memoria del juego | NO — pendiente (pixel reading) |
| Anti-detección | Ninguno | SLEEP jitter ±20% |
| Se rompe con updates | Sí (reflection names) | No (image recognition) |
| Riesgo de ban | Alto (inyección) | Bajo (solo simula input) |

## Limitaciones

1. **Necesita foco** — La ventana de PokéMMO debe estar activa. Auto-focus lo maneja, pero no puedes usar el PC para otra cosa.
2. **Image recognition frágil** — Las refs están calibradas para 1920x1080. Otra resolución/idioma/zoom = recapturar refs.
3. **Sin detección de HP** — No detecta HP bajo ni whiteout. Si el Pokemon se debilita, el bot puede desincronizarse.
4. **Sin detección de PP** — Si se acaban los PP, usa Struggle y se daña a sí mismo.
