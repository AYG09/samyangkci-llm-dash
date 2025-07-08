@echo off
REM Dash 앱 실행 (PYTHONPATH 자동 설정)
cd /d %~dp0
set PYTHONPATH=.
start "" http://127.0.0.1:8050/
python main.py
pause
