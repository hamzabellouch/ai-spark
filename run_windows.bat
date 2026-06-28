@echo off
if "%~1"=="-run" goto :run
cmd /c "%~f0" -run
goto :eof

:run
setlocal
cd /d "%~dp0"

REM Initialize PYTHON_CMD variable
set "PYTHON_CMD="

REM Check if 'py' works and can run python code
py -c "import sys" >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py"
) else (
  REM Check if 'python' works and can run python code
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

REM Set up virtual environment if it doesn't exist
if not exist .venv_windows (
  echo [AI Spark] Creating Python virtual environment .venv_windows for Windows...
  "%PYTHON_CMD%" -m venv .venv_windows
)

echo [AI Spark] Activating virtual environment...
call .venv_windows\Scripts\activate.bat

echo [AI Spark] Installing/updating requirements...
pip install -r src\requirements.txt
if errorlevel 1 (
  echo ERROR: Failed to install Python requirements.
  pause
  exit /b 1
)
REM Free up port 8000 if it's already in use by a stale Python process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr LISTENING ^| findstr :8000') do (
  echo [AI Spark] Port 8000 is occupied by process PID %%a. Terminating it to free the port...
  taskkill /f /pid %%a >nul 2>nul
)

:loop
echo.
echo Starting AI Spark on http://127.0.0.1:8000
echo Keep this window open while using the program.
echo.
powershell -Command "cd src; & python main.py"

:ask
set "choice="
set /p choice=Terminate AI Spark (y/n)? 
if /i "%choice%"=="y" goto end
if /i "%choice%"=="n" goto loop
goto ask

:end
