@echo off
cd /d D:\live-pnl-dashboard

:loop
echo [%time%] 🔁 Running sync_and_push.py...
python sync_and_push.py

echo [%time%] ⏳ Waiting 10 sec...
timeout /t 10 >nul

goto loop
