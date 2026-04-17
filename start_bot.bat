@echo off
:restart
python kino_bot.py
echo Bot o‘chdi, qayta yoqilyapti...
timeout /t 5
goto restart
