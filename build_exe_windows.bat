@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo [1/3] 正在安装打包工具...
py -3 -m pip install --upgrade pyinstaller pillow
if errorlevel 1 goto failed

echo [2/3] 正在生成独立的奶蛋.exe...
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "奶蛋" ^
  --icon "assets\奶蛋.ico" ^
  --add-data "assets;assets" ^
  pet.py
if errorlevel 1 goto failed

echo [3/3] 完成！
copy /Y "dist\奶蛋.exe" "奶蛋.exe" >nul
echo.
echo 已生成：%CD%\奶蛋.exe
echo 以后可以直接双击奶蛋.exe，不再需要 Python。
pause
exit /b 0

:failed
echo.
echo 打包失败。请保留此窗口并截取最后几行。
pause
exit /b 1
