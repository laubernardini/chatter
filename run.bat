@echo off
echo Iniciando chatter...
timeout /t 1 /nobreak > nul
cls
set /p bot_phone=Indica CELULAR (si no es business): 
set /p bot_server=Indica SERVER (dejar en blanco si no es CAT): 
set /p bot_grupos=Indica si envia solo a GRUPOS (SI/NO): 
set /p bot_desc=DESCRIPCION: 
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
if not "%bot_grupos%" == "" (
	set grupos=-g %bot_grupos%
)
if "%bot_grupos%" == "" (
	set grupos= 
)
if not "%bot_desc%" == "" (
	set desc=-d ^"%bot_desc%"
)
if "%bot_desc%" == "" (
	set desc= 
)
timeout /t 0 /nobreak > nul
cmd /k "git pull bot master & cd /d ..\vbot\scripts & activate & cd /d ..\..\bot & python run.py %phone% %server% %grupos% %desc%"