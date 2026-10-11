@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
    if not errorlevel 1 goto verify
)

py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if not errorlevel 1 (
    py -3 -m venv --without-pip .venv
    if errorlevel 1 goto failed
    goto verify
)

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 goto failed
python -m venv --without-pip .venv
if errorlevel 1 goto failed

:verify
".venv\Scripts\python.exe" -c "import csv, decimal, hashlib, json; from bank import Bank; print('Python and assignment modules are ready.')"
if errorlevel 1 goto failed

echo Setup complete. No extra Python packages are needed.
echo Open this folder in VS Code, install its recommended extensions, and press F5.
echo You can also double-click run.bat.
pause
exit /b 0

:failed
echo Setup failed. Install Python 3.10 or newer and run setup.bat again.
pause
exit /b 1
