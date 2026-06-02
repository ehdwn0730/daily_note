@echo off
setlocal

cd /d C:\workspace\research-note-automation

set LOG_DIR=C:\workspace\research-note-automation\logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set LOG_FILE=%LOG_DIR%\daily_html.log

echo ========================================== >> "%LOG_FILE%"
echo Daily HTML Research Note Automation >> "%LOG_FILE%"
echo Started at %DATE% %TIME% >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"

call .daily_note\Scripts\activate >> "%LOG_FILE%" 2>&1

echo [1/3] Collect daily context... >> "%LOG_FILE%"
python scripts\collect_daily_context.py >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo Failed to collect daily context. >> "%LOG_FILE%"
    exit /b 1
)

echo [2/3] Generate daily markdown note... >> "%LOG_FILE%"
python scripts\generate_daily_note.py >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo Failed to generate daily note. >> "%LOG_FILE%"
    exit /b 1
)

echo [3/3] Render daily HTML... >> "%LOG_FILE%"
python scripts\render_daily_html.py >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo Failed to render daily HTML. >> "%LOG_FILE%"
    exit /b 1
)

for /f "tokens=1-3 delims=/ " %%a in ("%DATE%") do (
    set YYYY=%%a
    set MM=%%b
    set DD=%%c
)

echo Opening HTML report... >> "%LOG_FILE%"

forfiles /p "C:\workspace\research-note-automation\html" /m "*.html" /d 0 /c "cmd /c start \"\" @path"

echo Completed at %DATE% %TIME% >> "%LOG_FILE%"
exit /b 0