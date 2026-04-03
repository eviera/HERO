#!/bin/bash
cd "$(dirname "$0")"

echo "===================================="
echo " H.E.R.O. - Instalador (Mac)"
echo "===================================="
echo

# Verificar que Python3 esté instalado
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 no está instalado o no está en el PATH."
    echo "Descargalo de https://www.python.org/downloads/"
    exit 1
fi

# Crear venv si no existe
if [ ! -f "venv/bin/activate" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo crear el entorno virtual."
        exit 1
    fi
    echo "Entorno virtual creado."
else
    echo "Entorno virtual ya existe."
fi

# Activar venv e instalar dependencias
echo "Instalando dependencias..."
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo
echo "===================================="
echo " Instalacion completa!"
echo " Usa ./hero.sh para jugar"
echo " Usa ./editor.sh para editar niveles"
echo "===================================="
