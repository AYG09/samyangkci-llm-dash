@echo off
REM requirements.txt 파일을 사용하여 모든 필수 라이브러리를 설치합니다.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo 라이브러리 설치가 완료되었습니다.
pause
