@echo off
echo Building HumankindApp...
echo.

where dotnet >nul 2>&1
if errorlevel 1 (
    echo [ERROR] .NET SDK not found.
    echo Install .NET 8 SDK from: https://dotnet.microsoft.com/download/dotnet/8.0
    pause
    exit /b 1
)

echo Building Release configuration...
dotnet build HumankindApp -c Release --nologo

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

set "APP_EXE="
for /f "delims=" %%f in ('dir /b /s "HumankindApp\bin\Release\HumankindApp.exe" 2^>nul') do (
    set "APP_EXE=%%f"
    goto :found_exe
)
:found_exe

echo.
echo ============================================
echo Build successful!
echo ============================================
echo.
echo Executable location:
if defined APP_EXE (
    echo   %APP_EXE%
) else (
    echo   (could not auto-detect; check HumankindApp\bin\Release\...)
)
echo.

set /p LAUNCH="Launch HumankindApp now? (y/n): "
if /i "%LAUNCH%"=="y" (
    if defined APP_EXE (
        start "" "%APP_EXE%"
    ) else (
        echo [ERROR] Could not locate HumankindApp.exe under HumankindApp\bin\Release
        pause
        exit /b 1
    )
)
