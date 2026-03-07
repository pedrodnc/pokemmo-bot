@echo off
REM ============================================
REM Setup PokéMMO Bot en Windows VPS
REM Ejecutar como Administrador
REM ============================================

echo === PokéMMO Bot - Setup Windows VPS ===

REM 1. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Instala Python 3.10+ desde python.org
    echo         Marca "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

REM 2. Verificar Java
java --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Java no encontrado. Instala Java 17+ desde adoptium.net
    pause
    exit /b 1
)

REM 3. Instalar dependencias del bot
echo [1/3] Instalando dependencias Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Fallo instalando dependencias
    pause
    exit /b 1
)

REM 4. Verificar PokéMMO
echo [2/3] Verificando PokéMMO...
if exist "C:\Program Files\PokeMMO\pokemmo-client.jar" (
    echo   PokéMMO encontrado
) else (
    echo   PokéMMO NO encontrado en C:\Program Files\PokeMMO
    echo   Descarga desde https://pokemmo.com/download e instala
)

REM 5. Crear script de arranque
echo [3/3] Creando script de arranque...
(
echo @echo off
echo cd /d "%~dp0"
echo echo Iniciando PokéMMO Bot...
echo echo Pulsa ESC para parar, P para pausar
echo python src/main.py
echo pause
) > run_bot.bat

echo.
echo === Setup completado ===
echo.
echo Pasos siguientes:
echo   1. Abre PokéMMO y haz login
echo   2. Configura: resolucion 1920x1080, keybinds (Z=A, X=B, flechas=movimiento)
echo   3. Posicionate en el Centro Pokemon
echo   4. Ejecuta run_bot.bat
echo.
echo Para modo agente IA:
echo   set ANTHROPIC_API_KEY=sk-ant-...
echo   Edita config.toml: [bot] MODE = "agent", [ai] ENABLED = true
echo.
pause
