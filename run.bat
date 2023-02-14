@echo off
echo Iniciando chatter...
timeout /t 2 /nobreak > nul
cls
set /p bot_phone=Indica CELULAR (si no es business): 
if not "%bot_phone%" == "" (
	set phone=-c %bot_phone%
)
if "%bot_phone%" == "" (
	set phone= 
)
timeout /t 2 /nobreak > nul
cmd /k "cd /d ..\vbot\scripts & activate & cd /d ..\..\bot & python run.py %phone%"