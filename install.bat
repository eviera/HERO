@echo off
cd /d "%~dp0"

echo ====================================
echo  H.E.R.O. - Instalador
echo ====================================
echo.

:: Verificar que Python este instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo Descargalo de https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Crear venv si no existe
if not exist "venv\Scripts\activate.bat" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo Entorno virtual creado.
) else (
    echo Entorno virtual ya existe.
)

:: Activar venv
call venv\Scripts\activate.bat

:: Instalar dependencias desde requirements.txt
echo Instalando dependencias...
pip install -r requirements.txt

call deactivate

echo.
echo ====================================
echo  Instalacion completa!
echo  Usa hero.bat para jugar
echo  Usa editor.bat para editar niveles
echo ====================================
pause
