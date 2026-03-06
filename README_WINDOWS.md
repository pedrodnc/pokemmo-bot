# PokéMMO Bot - Guía Windows

## Setup rápido

1. Clona el repo
2. Ejecuta `setup_windows.bat` (instala Python deps automáticamente)

## Configuración del juego OBLIGATORIA

Antes de ejecutar el bot, el juego tiene que estar así:

| Setting | Valor |
|---------|-------|
| Resolución | **1920 x 1080** |
| Modo | **Ventana** (no fullscreen) |
| Tecla Acción (A) | **Z** |
| Tecla Acción (B) | **X** |
| Movimiento | **Flechas del teclado** |

> Menú del juego → Options → Video → Resolution

## Scripts disponibles

### Para early game (sin Surf) ✅
```
scripts/Exp/Route2_EarlyUnova.txt
```
- Farming en hierba de Route 2 (Unova)
- Requisito: estar parado encima de la puerta del Centro Pokémon de Accumula Town

### Para mid/late game (requiere Surf HM) 
```
scripts/Exp/Spiraria.txt
```
- Farming en agua en Striaton City
- Requiere HM Surf (lo consigues al avanzar)

## Cómo ejecutar

```bash
python src/main.py
```

El bot te mostrará un menú para seleccionar el script.

O para ejecutarlo directamente:
Edita la línea en `src/main.py`:
```python
scriptPath = './scripts/Exp/Route2_EarlyUnova.txt'
```

## Controles durante la ejecución

| Tecla | Acción |
|-------|--------|
| `P` | Pausar / Reanudar |
| `ESC` | Parar el bot |

## Posición inicial para Route2_EarlyUnova

Tienes que estar aquí antes de ejecutar el bot:

```
Accumula Town → Pokémon Center
Posición: justo encima de la puerta del Centro (un paso arriba de la entrada)
```

El bot se moverá solo al centro a curar, luego bajará a la hierba de Route 2.

## Calibración de imágenes (si falla)

Si el bot se queda colgado en un WAITFOR, significa que la imagen de referencia no coincide con tu pantalla.

Las imágenes de referencia están en `refs/`. Si necesitas recalibrarlas:

1. Ejecuta el juego a 1920x1080
2. Llega al estado que falla (por ejemplo, pantalla de batalla)
3. Haz una captura de pantalla (Win + Shift + S)
4. Recorta **solo** el elemento que el bot busca (la flecha de diálogo, el menú Yes/No, etc.)
5. Guárdalo con el mismo nombre en `refs/`

## Imágenes de referencia y qué representan

| Archivo | Qué detecta |
|---------|-------------|
| `center.png` | Puerta del Centro Pokémon |
| `lotta.png` | Pantalla de inicio de batalla |
| `arrow.png` | Flecha de diálogo (▶) |
| `yesno.png` | Menú Sí/No |
| `terrain.png` | Mapa normal (sin batalla) |
| `mare.png` | Agua/mar en el mapa |
| `sassi2.png` | Rocas de referencia (script Spiraria) |
