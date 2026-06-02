@echo off
setlocal

set LATEST_PATH_FILE=C:\workspace\research-note-automation\html\latest_daily_html_path.txt

if exist "%LATEST_PATH_FILE%" (
    set /p HTML_PATH=<"%LATEST_PATH_FILE%"
    start "" "%HTML_PATH%"
) else (
    echo [ERROR] latest_daily_html_path.txt not found.
    echo 먼저 일일연구노트_생성_열기.bat을 실행하세요.
    pause
    exit /b 1
)

exit /b 0