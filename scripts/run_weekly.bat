@echo off
setlocal

cd /d C:\workspace\research-note-automation

echo ==========================================
echo Weekly Report Automation
echo ==========================================

call .venv\Scripts\activate

echo [1/2] Collect weekly context...
python scripts\collect_weekly_context.py

if errorlevel 1 (
    echo Failed to collect weekly context.
    pause
    exit /b 1
)

echo [2/2] Generate weekly report with Codex...
python scripts\generate_weekly_report.py

if errorlevel 1 (
    echo Failed to generate weekly report.
    pause
    exit /b 1
)

echo.
echo Weekly report generated successfully.
pause