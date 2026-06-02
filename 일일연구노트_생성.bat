@echo off
setlocal

cd /d C:\workspace\research-note-automation

echo ==========================================
echo Daily Research Note HTML
echo ==========================================
echo.

echo [1/4] Activate virtual environment...
call .daily_note\Scripts\activate

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to activate virtual environment.
    echo Check: C:\workspace\research-note-automation\.daily_note
    pause
    exit /b 1
)

echo.
echo [2/4] Collect daily context...
python scripts\collect_daily_context.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to collect daily context.
    pause
    exit /b 1
)

echo.
echo [3/4] Generate daily markdown note with Codex...
python scripts\generate_daily_note.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to generate daily note.
    pause
    exit /b 1
)

echo.
echo [4/4] Render HTML...
python scripts\render_daily_html.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to render HTML.
    pause
    exit /b 1
)

set LATEST_PATH_FILE=C:\workspace\research-note-automation\html\latest_daily_html_path.txt

if exist "%LATEST_PATH_FILE%" (
    set /p HTML_PATH=<"%LATEST_PATH_FILE%"
    echo.
    echo Opening:
    echo %HTML_PATH%
    start "" "%HTML_PATH%"
) else (
    echo.
    echo [ERROR] latest_daily_html_path.txt not found.
    pause
    exit /b 1
)

echo.
echo Done.
pause