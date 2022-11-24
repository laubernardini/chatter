@echo off
echo Iniciando bot...
timeout /t 2 /nobreak > nul
cls
set /p bot_pk=Indica BOT_PK: 
set /p bot_phone=Indica CELULAR (se puede dejar en blanco si es business): 
set /p bot_server=Indica SERVER (dejar en blanco si no es CAT): 
set /p bot_browser=Indica BROWSER ("f" para firefox "o" para opera): 
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
if not "%bot_browser%" == "" (
	set browser=-br %bot_browser%
)
if "%browser%" == "" (
	set bot_browser= 
)
timeout /t 2 /nobreak > nul
cmd /k "cd /d ..\vbot\scripts & activate & cd /d ..\..\bot & python run.py -b %bot_pk% %phone% %server% %browser%"