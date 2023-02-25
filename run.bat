@echo off
echo Iniciando chatter...
timeout /t 1 /nobreak > nul
cls
set /p bot_phone=Indica CELULAR (si no es business): 
set /p bot_server=Indica SERVER (dejar en blanco si no es CAT): 
if not "%bot_phone%" == "" (
	set phone=-c %bot_phone%
)
if "%bot_phone%" == "" (
	set phone= 
)
if not "%bot_server%" == "" (
	set server=-s %bot_server%
)
if "%bot_server%" == "" (
	set server= 
)
timeout /t 0 /nobreak > nul
REM cmd /k "cd /d ..\vbot\scripts & activate & cd /d ..\..\bot & python run.py %phone% %server%"
cmd /k "git reset --hard & git pull bot master & cd /d ..\vbot\scripts & activate & cd /d ..\..\bot & python run.py %phone% %server%"