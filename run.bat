@echo off
cd /d "%~dp0"

:: 检测本地嵌入版 Python，其次系统 Python
if exist "%~dp0python\python.exe" (
    set "PY=%~dp0python\python.exe"
) else (
    set "PY=python"
)

set "HOST_IP=127.0.0.1"
set "FLASK_TEST_MODE=1"
cls
"C:\Users\seewo\AppData\Local\Programs\Python\Python313\python.exe" "H:\Udisk\FKHL\FKHL-Release1.1.2\app.py"
pause
