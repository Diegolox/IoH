@echo off
python "%~dp0re_etiquetador.py" %*
if errorlevel 1 pause
