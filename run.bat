@echo off
cd /d "%~dp0"

echo ================================
echo    Cyber Pet
echo ================================
echo.
echo [1] TUI Mode
echo [2] CLI Mode
echo [3] Exit
echo.

set /p choice="Select (1/2/3): "

if "%choice%"=="1" (
    python main.py --tui
) else if "%choice%"=="2" (
    python main.py
) else if "%choice%"=="3" (
    exit
) else (
    python main.py
)

pause
