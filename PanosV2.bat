@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

rem Create venv if missing
if not exist "%VENV_PYTHON%" (
    echo [bootstrap] Creating virtual environment...
    where py >nul 2>nul
    if %errorlevel%==0 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
)

rem Clear proxy vars for yt-dlp/ffmpeg stability
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=
set NO_PROXY=
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

rem Bootstrap runtime and refresh yt-dlp periodically
"%VENV_PYTHON%" "%~dp0scripts\bootstrap_runtime.py"

rem Launch bot and replace stale/duplicate project instances automatically
"%VENV_PYTHON%" "%~dp0scripts\launch_panos.py"
set EXITCODE=%ERRORLEVEL%

if not "%EXITCODE%"=="0" (
    echo [runtime] bot exited with code %EXITCODE%
    pause
)
