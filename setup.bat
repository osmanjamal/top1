@echo off
echo Setting up Trading Platform Development Environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python first.
    exit /b 1
)

REM Check if virtualenv is installed
pip show virtualenv >nul 2>&1
if errorlevel 1 (
    echo Installing virtualenv...
    pip install virtualenv
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed. Please install Node.js first.
    exit /b 1
)

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm run install:all

REM Create necessary directories
echo Creating necessary directories...
mkdir backend\app\logs 2>nul
mkdir backend\app\static 2>nul
mkdir backend\app\media 2>nul

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.template .env >nul
)

echo Setup completed successfully!
echo To activate the virtual environment, run:
echo venv\Scripts\activate.bat