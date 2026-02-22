@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python editor.py
call deactivate
