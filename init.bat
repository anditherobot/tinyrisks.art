@echo off
cd /d "%~dp0"

:: Check if venv exists
if not exist "venv" (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Is Python installed and in your PATH?
        pause
        exit /b 1
    )
    echo [INFO] 'venv' created successfully.
) else (
    echo [INFO] Virtual environment 'venv' found.
)

:: Activate venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: Check for requirements.txt and install
if exist "requirements.txt" (
    echo [INFO] Installing/Updating dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found. Skipping dependency installation.
)

:: Run the application
echo [INFO] Starting Flask application...
python app.py

pause
