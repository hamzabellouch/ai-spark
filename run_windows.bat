@echo off
setlocal
cd /d "%~dp0"

:: Initialize PYTHON_CMD variable
set "PYTHON_CMD="

:: Check if 'py' works and can run python code
py -c "import sys" >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py"
) else (
  :: Check if 'python' works and can run python code
  python -c "import sys" >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON_CMD=python"
  )
)

if "%PYTHON_CMD%"=="" (
  echo ERROR: Python was not found or is not working properly.
  echo Please make sure you have Python 3.11 or newer installed from https://www.python.org/
  echo and make sure to check the option "Add python.exe to PATH" during installation.
  echo.
  pause
  exit /b 1
)

echo [AI Spark] Using Python command: "%PYTHON_CMD%"

echo [AI Spark] Installing/updating requirements...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERROR: Failed to install Python requirements.
  pause
  exit /b 1
)
:: Free up port 8000 if it's already in use by a stale Python process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr LISTENING ^| findstr :8000') do (
  echo [AI Spark] Port 8000 is occupied by process PID %%a. Terminating it to free the port...
  taskkill /f /pid %%a >nul 2>nul
)

echo.
echo Starting AI Spark on http://127.0.0.1:8000
echo Keep this window open while using the program.
echo.
%PYTHON_CMD% main.py


pause
