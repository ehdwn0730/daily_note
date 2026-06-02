@echo off
setlocal

cd /d C:\workspace\research-note-automation

echo ==========================================
echo Daily Research Note Automation
echo ==========================================

call .venv\Scripts\activate

echo [1/2] Collect daily context...
python scripts\collect_daily_context.py

if errorlevel 1 (
    echo Failed to collect daily context.
    pause
    exit /b 1
)

echo [2/2] Generate daily note with Codex...
python scripts\generate_daily_note.py

if errorlevel 1 (
    echo Failed to generate daily note.
    pause
    exit /b 1
)

echo.
echo Daily note generated successfully.
pause