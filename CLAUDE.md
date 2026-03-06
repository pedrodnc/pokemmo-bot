# CLAUDE.md - PokéMMO Bot

## Qué es esto

Bot de farming automático para PokéMMO (cliente MMO basado en Pokémon Gen 3-5).
Fork de [caamillo/alphaForny](https://github.com/caamillo/alphaForny) con scripts adicionales para Unova early game.

## Arquitectura

```
src/
  main.py           → Entrada. Carga config, selecciona script, arranca AlphaForny
  AlphaForny.py     → Clase principal. Gestiona threads (ejecución + input listener)
  FornyTranslator.py → Parsea los scripts .txt y traduce comandos a acciones
  Action.py         → Ejecuta acciones reales: teclado, ratón, image recognition
  Config.py         → Lee config.toml
  Script.py         → Navegador de scripts en menú interactivo
  Language.py       → i18n (en.json / it.json)

scripts/
  Exp/
    Route3_Striaton.txt    → Farm early Unova (Striaton City → Route 3) ← ACTIVO
    Route2_EarlyUnova.txt  → Farm early Unova (Accumula Town → Route 2)
    Spiraria.txt           → Farm mid-late (requiere HM Surf)
  Gym/Unima/
    All.txt                → Gym rematch Unova (vacío, sin implementar)
    Levantopoli.txt        → Gym rematch Castelia (vacío)
  EVs/Unima/               → Scripts de EV training (no incluidos en este fork)

refs/                      → Imágenes de referencia para image recognition (1920x1080)
  center.png    → Puerta Centro Pokémon
  lotta.png     → Pantalla de inicio de batalla
  arrow.png     → Flecha de diálogo (▶)
  yesno.png     → Menú Sí/No
  terrain.png   → Mapa (sin batalla)
  mare.png      → Agua en el mapa
  sassi.png     → Roca de referencia (Spiraria)
  sassi2.png    → Roca de referencia 2 (Spiraria)
  hp.png        → Barra de HP
  dialogue.png  → Cuadro de diálogo genérico
  duesassi.png  → Dos rocas (Spiraria)
```

## Cómo funciona el DSL de scripts

Los scripts .txt tienen dos secciones: `setup:` (se ejecuta una vez) y `loop:` (bucle infinito).

Comandos disponibles:
```
PRESS <key>           → Pulsa y suelta una tecla
HOLD <key>            → Mantiene pulsada una tecla
RELEASE <key>         → Suelta una tecla
SLEEP <segundos>      → Espera N segundos (acepta decimales)
WAITFOR <ref>         → Espera hasta detectar refs/<ref>.png en pantalla
UNTIL <ref>           → Espera hasta que refs/<ref>.png DEJE de aparecer
SPAM <key>            → Empieza a spamear una tecla en background thread
STOPSPAM <key>        → Para el spam
CLICK <x>,<y>         → Click de ratón en coordenadas absolutas
PRINT <texto>         → Log en consola
```

Teclas especiales: UP, DOWN, LEFT, RIGHT, SHIFT. El resto son caracteres literales (z, x, j...).

## Estado actual

- Script activo: `Route3_Striaton.txt`
- Región: Unova
- Punto de inicio: Centro Pokémon de Striaton City (1er gym)
- Requiere: Python 3.10+, resolución 1920x1080, controles A=Z B=X flechas

## Limitaciones conocidas

1. **Image recognition frágil**: Las refs están calibradas para la pantalla del autor original. Si la resolución, zoom o idioma del juego difiere, los WAITFOR se cuelgan indefinidamente.
2. **Timing fijo**: Los SLEEP están hardcodeados. Si el PC es lento o el servidor tiene lag, el personaje puede desincronizarse del camino esperado.
3. **Sin detección de HP**: El bot no detecta cuándo el Pokémon está débil — confía en que el loop de curación en el Centro funcione a tiempo.
4. **Sin anti-ban**: Los delays son fijos y predecibles. Para uso prolongado, añadir variación aleatoria en los SLEEP.

## Mejoras prioritarias

Si trabajas en este proyecto, estas son las mejoras más útiles por orden:

1. **Delays aleatorios**: Cambiar `SLEEP 1.5` por `SLEEP random(1.2, 1.8)` en FornyTranslator
2. **Detección de HP crítico**: Usar `WAITFOR hp` para detectar HP bajo y forzar vuelta al centro antes del loop normal
3. **Config de keybinds en config.toml**: Que Action.py lea las teclas de config en vez de estar hardcodeadas
4. **Timeout en WAITFOR**: Si tarda más de N segundos, reiniciar desde el centro en vez de colgarse
5. **Logging de sesión**: Guardar XP/hora, batallas ganadas, tiempo total

## Setup en Windows

```bat
setup_windows.bat   # instala deps
python src/main.py  # ejecuta el bot
```

Ver `README_WINDOWS.md` para instrucciones completas.
