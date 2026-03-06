# CLAUDE.md - Perfil de usuario (global)

> Copia este archivo a `C:\Users\<tuusuario>\.claude\CLAUDE.md` en Windows
> o a `~/.claude/CLAUDE.md` en Linux/Mac para que Claude Code lo lea en todos los proyectos.

## Sobre mí

Desarrollador con experiencia en ciberseguridad ofensiva y desarrollo web.
Trabajo principalmente en Windows con WSL2 (Kali Linux) y VS Code con Remote-SSH.
Idioma preferido: español. Código y términos técnicos en inglés.

## Estilo de respuesta

- Directo y sin rodeos. No expliques conceptos básicos.
- Código mínimo y preciso — no bloques enteros cuando basta un diff o una línea.
- Si algo está mal o el enfoque es cuestionable, dímelo.
- Dame la mejor opción primero. Alternativas solo si son relevantes.
- No hagas introducciones ni cierres tipo "espero que te sirva".

## Stack habitual

- Python 3.10+
- Node.js / Vite / React
- VPS Ubuntu 24.04 (DigitalOcean)
- Kali Linux en WSL2
- VS Code + Remote-SSH
- Git / GitHub (usuario: pedrodnc)

## Proyectos activos

### pokemmo-bot
Bot de farming automático para PokéMMO escrito en Python.
Basado en image recognition con pyautogui + pynput.
Arquitectura DSL: scripts .txt con comandos PRESS/HOLD/WAITFOR/SPAM/SLEEP.
Región activa: Unova. Script activo: Route3_Striaton.txt.
Repo: https://github.com/pedrodnc/pokemmo-bot

### denacomparamos
Scraper + frontend de comparación de precios para productos de juego.
Stack: Node.js (scraper) + Vite/React (frontend) + Cloudflare Workers/D1.
Repo: https://github.com/pedrodnc/denacomparamos

## Conocimiento de dominio: PokéMMO bot development

PokéMMO es un cliente MMO que reimplementa los juegos de Pokémon Gen 3, 4 y 5.
Para desarrollar bots en PokéMMO, el contexto relevante es:

### Mecánicas del juego relevantes para bots

- **Encuentros salvajes**: caminar en hierba alta o usar Surf en agua trigonometría aleatoria (~1 cada 5-20 pasos)
- **Centro Pokémon**: cura todo el equipo gratis, infinitas veces. Es el ancla de cualquier loop de farming
- **HMs**: movimientos especiales que actúan como llaves de zonas. Surf (agua), Cut (arbustos), Fly (viaje rápido)
- **Hordas**: en PokéMMO se puede usar Sweet Scent para invocar batalla de 5 Pokémon a la vez → más XP/hora
- **Gym rematch**: los entrenadores de gimnasio se pueden revocar periódicamente → fuente estable de XP
- **EV training**: cada especie da EVs específicos al derrotarla. El farming de EVs requiere matar siempre la misma especie

### Enfoques de bot para PokéMMO

1. **Image recognition** (pyautogui): compara capturas de pantalla con imágenes de referencia. Frágil, dependiente de resolución. No requiere modificar el cliente.
2. **Input simulation** (pyautogui/pynput/AHK): simula teclado y ratón. Se combina con el anterior.
3. **Java Reflection** (RedTrainer): se inyecta en el proceso Java de PokéMMO vía reflection. Más robusto, puede leer estado interno del juego, funciona con ventana sin foco.
4. **Pixel reading**: leer colores de píxeles específicos en vez de comparar imágenes completas. Más rápido y menos frágil que image recognition.

### Anti-detección

PokéMMO tiene anticheat pasivo basado en patrones de comportamiento:
- Delays exactamente iguales → sospechoso
- Siempre el mismo movimiento → sospechoso
- Horas de actividad continua sin pausa → sospechoso

Mitigaciones:
- Randomizar sleeps (±10-20% variación)
- Añadir micro-pausas aleatorias
- Limitar sesiones de bot a 2-4 horas
- Variar rutas de movimiento

### Estructura de un script de farming efectivo

```
setup:
    ir al Centro Pokemon (HOLD + WAITFOR center)

loop:
    curar en centro (PRESS Z x N veces con WAITFOR entre medias)
    ir a zona de farming (HOLD dirección + SLEEP o WAITFOR landmark)
    provocar encuentros (zigzag en hierba o SURF en agua)
    ganar batalla (WAITFOR lotta + SPAM Z + WAITFOR terrain)
    volver al centro (HOLD dirección + WAITFOR center)
```

### Referencias para el DSL de scripts (pokemmo-bot)

```
PRESS <key>      → Pulsa y suelta
HOLD <key>       → Mantiene pulsada
RELEASE <key>    → Suelta
SLEEP <seg>      → Espera (acepta decimales)
WAITFOR <ref>    → Espera hasta ver refs/<ref>.png en pantalla
UNTIL <ref>      → Espera hasta que desaparezca
SPAM <key>       → Spamea en thread background
STOPSPAM <key>   → Para el spam
CLICK <x>,<y>    → Click en coordenadas absolutas
PRINT <texto>    → Log
```

Teclas especiales: UP DOWN LEFT RIGHT SHIFT. Resto: literal (z, x, j...).

### Imágenes de referencia (refs/) a 1920x1080

| Archivo | Detecta |
|---------|---------|
| center.png | Puerta Centro Pokémon |
| lotta.png | Inicio de batalla |
| arrow.png | Flecha de diálogo ▶ |
| yesno.png | Menú Sí/No |
| terrain.png | Mapa normal (sin batalla) |
| mare.png | Agua en el mapa |
| hp.png | Barra de HP |

Si un WAITFOR se cuelga, significa que la ref no coincide con la pantalla actual.
Solución: recapturar esa ref desde el juego a 1920x1080.
