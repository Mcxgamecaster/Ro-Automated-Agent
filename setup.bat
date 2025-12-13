@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Humankind Bot - Setup Script
echo ============================================
echo.

:: Check for Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+ and add it to PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo       Found Python %PYVER%

:: Create virtual environment
echo.
echo [2/4] Setting up Python virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo       Created .venv
) else (
    echo       .venv already exists, skipping creation
)

:: Activate and install dependencies
echo.
echo [3/4] Installing Python dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo       Dependencies installed

:: Build WPF app
echo.
echo [4/4] Building HumankindApp (WPF GUI)...
where dotnet >nul 2>&1
if errorlevel 1 (
    echo [WARNING] .NET SDK not found. Skipping WPF app build.
    echo          Install .NET 8 SDK from: https://dotnet.microsoft.com/download/dotnet/8.0
    echo          Then run: dotnet build HumankindApp -c Release
) else (
    dotnet build HumankindApp -c Release --nologo -v q
    if errorlevel 1 (
        echo [ERROR] WPF build failed. Check .NET 8 SDK installation.
    ) else (
        echo       HumankindApp.exe built successfully
        echo       Location: HumankindApp\bin\Release\net8.0-windows10.0.19041.0\HumankindApp.exe
    )
)

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Next steps:
echo   1. Activate venv:  .venv\Scripts\activate
echo   2. Run calibration: python -m hk3_bot.calibration --config configs/humankind3.yaml --profile windowed
echo   3. Or use the GUI:  HumankindApp\bin\Release\net8.0-windows10.0.19041.0\HumankindApp.exe
echo.
pause
