@echo off
setlocal
pushd "%~dp0" || exit /b 1
python -m PyInstaller --noconfirm --onefile --console --exclude-module IPython --name IoH-Captura-03 --distpath "." --workpath ".compilacion\work" --specpath ".compilacion" imu_terminal.py
set "result=%errorlevel%"
popd
exit /b %result%
