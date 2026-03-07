"""
Herramienta interactiva para capturar las refs del bot.
Ejecutar desde la raiz del proyecto: python src/capture_refs.py

Te guia paso a paso por cada ref que necesitas capturar.
Seleccionas la zona con el raton y se guarda automaticamente.
"""

import os
import sys
import time

try:
    import pyautogui as pag
    from PIL import Image, ImageGrab
except ImportError:
    print("[ERROR] Instala dependencias: pip install pyautogui Pillow")
    sys.exit(1)

REFS_DIR = "./refs"
BACKUP_DIR = "./refs/backup"

REFS = [
    {
        "name": "center",
        "desc": "Puerta del Centro Pokemon",
        "instructions": [
            "1. Abre PokéMMO (1920x1080, ventana)",
            "2. Ve al Centro Pokemon que vayas a usar",
            "3. Sal fuera y mira la PUERTA del edificio",
            "4. Pulsa ENTER cuando estes listo...",
        ],
        "tip": "Recorta SOLO la puerta (cuadrado pequeno ~100x80px)",
    },
    {
        "name": "arrow",
        "desc": "Flecha de dialogo (triangulo)",
        "instructions": [
            "1. Entra al Centro Pokemon",
            "2. Habla con Nurse Joy (pulsa Z)",
            "3. Espera a que aparezca la flecha > en el dialogo",
            "4. Pulsa ENTER cuando veas la flecha...",
        ],
        "tip": "Recorta SOLO la flechita, nada de texto",
    },
    {
        "name": "yesno",
        "desc": "Menu Si/No de curacion",
        "instructions": [
            "1. Sigue hablando con Nurse Joy",
            "2. Espera al menu Si/No (Curar tu equipo?)",
            "3. Pulsa ENTER cuando veas el menu Si/No...",
        ],
        "tip": "Recorta el cuadro Si/No entero",
    },
    {
        "name": "lotta",
        "desc": "Pantalla de batalla (inicio de combate)",
        "instructions": [
            "1. Sal del centro y ve a la hierba",
            "2. Camina hasta provocar un encuentro salvaje",
            "3. Cuando aparezca la pantalla de batalla...",
            "4. Pulsa ENTER...",
        ],
        "tip": "Recorta la barra de HP enemiga o el marco de batalla. Algo UNICO de batalla",
    },
    {
        "name": "terrain",
        "desc": "Mapa normal (overworld, sin batalla)",
        "instructions": [
            "1. Gana la batalla (o huye)",
            "2. Vuelve al mapa normal",
            "3. Pulsa ENTER cuando estes en el mapa...",
        ],
        "tip": "Recorta un trozo del suelo/hierba que sea UNICO del mapa (no aparece en batalla)",
    },
    {
        "name": "hp",
        "desc": "Barra de HP de tu Pokemon en batalla (opcional)",
        "instructions": [
            "1. Entra en otra batalla",
            "2. Mira la barra de HP de TU Pokemon",
            "3. Pulsa ENTER...",
        ],
        "tip": "Recorta el marco/etiqueta de HP, no la barra verde (cambia segun vida)",
    },
]


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def capture_region():
    """Permite al usuario seleccionar una region de la pantalla con el raton."""
    print()
    print("  >> Selecciona la zona en pantalla:")
    print("     - Mueve el raton a la ESQUINA SUPERIOR IZQUIERDA y pulsa ENTER")

    input()
    x1, y1 = pag.position()
    print(f"     Esquina superior izquierda: ({x1}, {y1})")

    print("     - Mueve el raton a la ESQUINA INFERIOR DERECHA y pulsa ENTER")

    input()
    x2, y2 = pag.position()
    print(f"     Esquina inferior derecha: ({x2}, {y2})")

    # Validar
    if x2 <= x1 or y2 <= y1:
        print("  [ERROR] La segunda esquina debe estar abajo-derecha de la primera")
        return None

    width = x2 - x1
    height = y2 - y1
    print(f"     Tamano: {width}x{height}px")

    if width > 300 or height > 300:
        print("  [AVISO] El recorte es muy grande. Refs pequenas (80-150px) funcionan mejor.")
        resp = input("  Continuar de todos modos? (s/n): ").strip().lower()
        if resp != 's':
            return None

    # Capturar
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    return screenshot


def preview_ref(img, name):
    """Muestra info del recorte."""
    print(f"     Capturado: {img.size[0]}x{img.size[1]}px")

    # Guardar preview temporal
    preview_path = os.path.join(REFS_DIR, f"{name}_preview.png")
    img.save(preview_path)
    print(f"     Preview guardada en: {preview_path}")


def main():
    clear()
    print("=" * 60)
    print("  CAPTURA DE REFS - PokéMMO Bot")
    print("=" * 60)
    print()
    print("  Este asistente te guia para capturar las imagenes de")
    print("  referencia que el bot usa para reconocer el juego.")
    print()
    print("  Necesitas PokéMMO abierto en 1920x1080 (ventana).")
    print()
    print("  Para cada ref:")
    print("    1. Te digo que hacer en el juego")
    print("    2. Pones el raton en una esquina, ENTER")
    print("    3. Pones el raton en la otra esquina, ENTER")
    print("    4. Se guarda automaticamente")
    print()

    # Crear dirs
    os.makedirs(REFS_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Backup de refs existentes
    existing = [f for f in os.listdir(REFS_DIR) if f.endswith('.png') and not f.endswith('_preview.png')]
    if existing:
        print(f"  Se encontraron {len(existing)} refs existentes.")
        resp = input("  Hacer backup antes de reemplazar? (s/n): ").strip().lower()
        if resp == 's':
            import shutil
            for f in existing:
                src = os.path.join(REFS_DIR, f)
                dst = os.path.join(BACKUP_DIR, f)
                shutil.copy2(src, dst)
            print(f"  Backup guardado en {BACKUP_DIR}/")
        print()

    input("  Pulsa ENTER para empezar...")

    captured = []
    skipped = []

    for i, ref in enumerate(REFS):
        clear()
        print(f"  [{i + 1}/{len(REFS)}] {ref['name'].upper()} — {ref['desc']}")
        print("  " + "-" * 50)
        print()

        for line in ref['instructions']:
            print(f"  {line}")
        print()
        print(f"  TIP: {ref['tip']}")

        # Opcion de saltar
        print()
        print("  (Pulsa ENTER para capturar, o escribe 'skip' para saltar)")
        resp = input("  > ").strip().lower()

        if resp == 'skip':
            skipped.append(ref['name'])
            print(f"  Saltado: {ref['name']}")
            time.sleep(0.5)
            continue

        # Capturar
        img = capture_region()
        if img is None:
            print("  Captura cancelada, reintentando...")
            time.sleep(1)
            # Reintentar
            img = capture_region()

        if img is None:
            skipped.append(ref['name'])
            print(f"  Saltado: {ref['name']}")
            time.sleep(1)
            continue

        # Guardar
        path = os.path.join(REFS_DIR, f"{ref['name']}.png")
        img.save(path)
        captured.append(ref['name'])
        print(f"  Guardado: {path} ({img.size[0]}x{img.size[1]}px)")

        # Limpiar preview si existe
        preview = os.path.join(REFS_DIR, f"{ref['name']}_preview.png")
        if os.path.exists(preview):
            os.remove(preview)

        time.sleep(0.5)

    # Resumen
    clear()
    print()
    print("=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print()
    for name in captured:
        print(f"  OK  {name}.png")
    for name in skipped:
        print(f"  --  {name}.png (saltado)")

    print()
    if skipped:
        print(f"  AVISO: Faltan {len(skipped)} refs. El bot puede fallar sin ellas.")
        print(f"  Ejecuta este script de nuevo para capturar las que faltan.")
    else:
        print("  Todas las refs capturadas. El bot esta listo.")

    print()
    print("  Siguiente paso:")
    print("    python src/main.py")
    print()


if __name__ == "__main__":
    main()
