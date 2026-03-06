@echo off
echo ========================================
echo   PokéMMO Bot - Setup Windows
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instala Python 3.10+ desde https://python.org
    echo        Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

echo [OK] Python encontrado.
echo.

REM Install deps
echo Instalando dependencias...
pip install pyautogui==0.9.53 pynput==1.7.6 toml==0.10.2 pillow
if errorlevel 1 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)

echo.
echo [OK] Dependencias instaladas.
echo.
echo ========================================
echo   ANTES DE EJECUTAR EL BOT:
echo ========================================
echo.
echo 1. Abre PokeMMMO
echo 2. Pon la resolucion del juego en 1920x1080
echo    (Options - Video - Resolution)
echo 3. Pon el juego en modo VENTANA (no fullscreen)
echo 4. Asegurate de que los controles son:
echo    - Movimiento: Flechas del teclado
echo    - Accion (A): Z
echo    - Accion (B): X
echo 5. Ejecuta: python src/main.py
echo.
echo ========================================
pause
