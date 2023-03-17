@echo off
echo Iniciando chatter...
timeout /t 1 /nobreak > nul
cls
set /p bot_phone=Indica CELULAR (si no es business): 
set /p bot_server=Indica SERVER (dejar en blanco si no es CAT): 
set /p bot_desc=DESCRIPCION: 
echo ----
set /p bot_grupos=Indica si envia solo a GRUPOS (SI/NO): 
set /p bot_lista_grupos=Indica numero de lista de GRUPOS (numero): 
echo ----
set /p bot_tiempo=Tiempo entre envios (5min p. def.): 
set /p bot_tiempo_modo=Tiempo para cambio de modo (20min p. def.): 
echo ----

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

if not "%bot_lista_grupos%" == "" (
	set lista_grupos=-lg %bot_lista_grupos%
)
if "%bot_lista_grupos%" == "" (
	set lista_grupos= 
)

if not "%bot_tiempo%" == "" (
	set tiempo=-t %bot_tiempo%
)
if "%bot_tiempo%" == "" (
	set tiempo= 
)

if not "%bot_tiempo_modo%" == "" (
	set tiempo_modo=-tm %bot_tiempo_modo%
)
if "%bot_tiempo_modo%" == "" (
	set tiempo_modo= 
)

if not "%bot_desc%" == "" (
	set desc=-d ^"%bot_desc%"
)
if "%bot_desc%" == "" (
	set desc= 
)

cmd /k "git pull bot master & cd /d ..\vbot\scripts & activate & cd /d ..\..\bot & python run.py %phone% %server% %tiempo% %tiempo_modo% %grupos% %lista_grupos% %desc%"