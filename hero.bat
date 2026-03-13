@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python hero.py %*
call deactivate
