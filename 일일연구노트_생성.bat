@echo off
setlocal

cd /d C:\Users\ehdwn\Desktop\project\daily_note

echo ==========================================
echo Daily Research Note DOCX
echo ==========================================
echo.

echo [1/4] Activate virtual environment...
if exist ".daily_note\Scripts\activate.bat" (
    call .daily_note\Scripts\activate.bat
) else if exist ".daliy_note\Scripts\activate.bat" (
    call .daliy_note\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo.
    echo [ERROR] Virtual environment not found.
    echo Check: %CD%\.daily_note or %CD%\.daliy_note or %CD%\.venv
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to activate virtual environment.
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
echo [4/4] Update weekly DOCX from template...
python scripts\render_weekly_daily_docx.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to update weekly DOCX.
    pause
    exit /b 1
)

set LATEST_PATH_FILE=%CD%\documents\daily_note\latest_daily_note_docx_path.txt

if exist "%LATEST_PATH_FILE%" (
    set /p DOCX_PATH=<"%LATEST_PATH_FILE%"
    echo.
    echo Updated DOCX:
    echo %DOCX_PATH%
)

echo.
echo Done.
pause
