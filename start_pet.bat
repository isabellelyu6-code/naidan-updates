@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 goto use_py
where python >nul 2>&1
if not errorlevel 1 goto use_python

echo Python is not installed or Windows cannot find it.
echo Install Python and select Add python.exe to PATH.
pause
exit /b 1

:use_py
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto failed
start "" pyw -3 pet.py
if errorlevel 1 py -3 pet.py
exit /b 0

:use_python
python -m pip install -r requirements.txt
if errorlevel 1 goto failed
start "" pythonw pet.py
if errorlevel 1 python pet.py
exit /b 0

:failed
echo.
echo Installation failed. Take a screenshot of this window and send it to ChatGPT.
pause
exit /b 1
