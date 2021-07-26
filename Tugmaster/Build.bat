@echo off
chcp 65001
cd Backend
echo 正在构建计算服务端...
call Build.bat
echo 计算服务构建完成
echo.
cd ..
cd Frontend
echo 正在构建前端...
call Build.bat
echo 前端构建完成
echo.
pause
