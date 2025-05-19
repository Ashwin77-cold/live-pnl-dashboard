
@echo off
cd /d D:\live-pnl-dashboard

:loop
echo [%time%] 🔁 Running dashboard sync...
python sync_and_push.py

timeout /t 20 >nul
goto loop
