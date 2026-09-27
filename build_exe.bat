@echo off
chcp 65001 >nul
echo ========================================================
echo       Meeting Voice Copilot - Windows EXE 打包脚本
echo ========================================================
echo 正在检查 Python 环境与依赖...
pip install -r requirements.txt

echo.
echo 正在使用 PyInstaller 编译为 Windows 应用程序...
pyinstaller --noconfirm --onedir --windowed ^
    --name "MeetingVoiceCopilot" ^
    --add-data "ui;ui" ^
    --add-data "core;core" ^
    --clean ^
    app.py

echo.
echo ========================================================
echo 打包完成！可执行文件目录位于:
echo dist\MeetingVoiceCopilot\MeetingVoiceCopilot.exe
echo ========================================================
pause
