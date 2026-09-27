@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "AT8_DIR=%~dp0"
set "AT8_LAUNCHER=%~f0"
set "AT8_SHORTCUT=Autotrade 8 Observe.lnk"
set "PYTHONPATH=%AT8_DIR%src"
cd /d "%AT8_DIR%" || exit /b 1

if /I "%~1"=="run" goto run
if /I "%~1"=="uninstall" goto uninstall
if not "%~1"=="" if /I not "%~1"=="install" goto usage

:install
call :check_python || exit /b 1
echo Installing current-user Startup shortcut for observe-only replay...
powershell -NoProfile -NonInteractive -Command "$s=[Environment]::GetFolderPath('Startup'); if (-not $s) { throw 'Startup folder missing' }; $w=New-Object -ComObject WScript.Shell; $l=$w.CreateShortcut((Join-Path $s $env:AT8_SHORTCUT)); $l.TargetPath=$env:AT8_LAUNCHER; $l.Arguments='run'; $l.WorkingDirectory=$env:AT8_DIR; $l.Description='Autotrade 8 local observe-only replay'; $l.Save()"
if errorlevel 1 (
    echo Startup installation failed. No changes to trading state.
    exit /b 1
)
echo Installed for this Windows user. The dashboard will start at next sign-in.
echo Starting it now...
goto run

:uninstall
powershell -NoProfile -NonInteractive -Command "$s=[Environment]::GetFolderPath('Startup'); $p=Join-Path $s $env:AT8_SHORTCUT; if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Force }"
if errorlevel 1 exit /b 1
echo Startup shortcut removed. Close any existing dashboard window separately.
exit /b 0

:run
call :check_python || exit /b 1
%AT8_PY% -c "import socket; s=socket.socket(); x=s.connect_ex(('127.0.0.1', 8768)); s.close(); raise SystemExit(0 if x else 1)"
if errorlevel 1 (
    echo Port 8768 is already occupied. Avoiding a second dashboard instance.
    exit /b 1
)
echo.
echo Observe-only dashboard: http://127.0.0.1:8768
echo Built-in input is SYNTHETIC. No exchange connection or orders.
echo Closing the Python process unexpectedly restarts it in 10 seconds.
echo To stop the loop, close this console window. To remove sign-in startup,
echo run AUTOTRADE8_AUTOSTART.bat uninstall
echo.
:restart
%AT8_PY% -m autotrade8.app --port 8768
echo Dashboard exited with code %errorlevel%. Restarting in 10 seconds...
timeout /t 10 /nobreak >nul
goto restart

:check_python
set "AT8_PY=python"
where py >nul 2>nul && set "AT8_PY=py -3"
%AT8_PY% -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'; import autotrade8.app" >nul
if errorlevel 1 if "%AT8_PY%"=="py -3" (
    set "AT8_PY=python"
    python -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'; import autotrade8.app" >nul
)
if errorlevel 1 (
    echo Python 3.11+ or the application is missing. Install Python and keep this BAT inside the repo.
    exit /b 1
)
exit /b 0

:usage
echo Usage: AUTOTRADE8_AUTOSTART.bat [install^|run^|uninstall]
exit /b 2
