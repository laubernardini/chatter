import os

import urlfetch
import urllib
import json
import asyncio
import time

import bot

# Reporte
async def status():
    try:
        r = urlfetch.get(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/report?pk=" + str(bot.BOT_PK) + "&estado=" + str(bot.STATE), validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error enviando estado")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.STATE = "ERROR"
        bot.RESPONDE = bot.MASIVO = bot.AUTO = "NO"

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API status: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("     estado=" + str(bot.STATE))
            print("Response: " + str(r.content))

        content = json.loads(r.content)
        content = content[0]

        bot.RESPONDE = content["responde"]
        bot.MASIVO = content["masivo"]
        bot.AUTO = content["auto"]
        bot.THREAD = content["thread"]

    return r

# Obtener archivo
def get_file(url):
    if bot.SHOW_EX_PRINTS:
        print("Obteniendo archivo...")
    done = None
    s = bot.FILE_SERVER
    while not done:
        try:
            if bot.SHOW_EX_PRINTS:
                print("Intentando con " + s + url)
            r = urlfetch.get(s + url, validate_certificate=False)
            done = True
        except Exception as e:
            if s == bot.FILE_SERVER:
                s = bot.FILE_SERVER_2
            else:
                s = bot.FILE_SERVER
            if bot.SHOW_ERRORS:
                print(e)
            time.sleep(2)
    filename = url.rsplit('/', 1)[1]
    if not os.path.exists('file_cache'):
        os.makedirs('file_cache')
    open("file_cache/" + filename, "wb").write(r.content)

    return os.path.abspath('file_cache/' + filename)

# Respuestas manuales
def get_response():
    try:
        r = urlfetch.get(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/respuesta?pk=" + str(bot.BOT_PK), validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error obteniendo respuesta")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.STATE = "ERROR"
        bot.RESPONDE = bot.MASIVO = bot.AUTO = "NO"

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API get_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("Response: " + str(r.content))

        content = json.loads(r.content)
        r = content[0]
    else:
        r = {}

    return r

async def post_response(pk, estado):
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        fields = {}
        fields["pk"] = bot.BOT_PK
        fields["pk_respuesta"] = pk
        fields["estado"] = estado
        data = urllib.parse.urlencode(fields)
        
        r = urlfetch.post(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/respuesta", validate_certificate=False, headers=headers, data=data)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error confirmando respuesta")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.STATE = "ERROR"
        bot.RESPONDE = bot.MASIVO = bot.AUTO = "NO"

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API post_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("     pk_respuesta=" + str(pk))
            print("Response: " + str(r.content))

        content = json.loads(r.content)
        r = content[0]
    else:
        r = {}

    return r

# Respuestas automáticas
def get_auto_response(mensaje, celular):
    try:
        mensaje = urllib.parse.quote(mensaje)
        r = urlfetch.get(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/r-auto?pk=" +bot.BOT_PK + "&celular=" + celular + "&mensaje=" + mensaje, validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error obteniendo respuesta automática")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.STATE = "ERROR"
        bot.RESPONDE = bot.MASIVO = bot.AUTO = "NO"

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API get_auto_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("Response: " + str(r.content))
        
        content = json.loads(r.content)
        r = content[0]
        if r.get("response", "") != "" or r.get("archivo", "") != "":
            bot.AUTO_RESPONSES.append({
                "celular": celular,
                "mensaje": r.get("response", ""), 
                "archivo": r.get("archivo", "")
            })
    else:
        r = {}

async def post_auto_response(mensaje, celular, archivo):
    try:
        files = {}
        fields = {
            "pk": bot.BOT_PK,
            "celular": celular,
            "mensaje": mensaje
        }
        if archivo != "":
            files = {
                "archivo": open(archivo, 'rb')
            }
        r = urlfetch.post(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/r-auto", data=fields, files=files, validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error confirmando respuesta automática")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.STATE = "ERROR"
        bot.RESPONDE = bot.MASIVO = bot.AUTO = "NO"

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API post_auto_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("Response: " + str(r.content))
    else:
        r = {}

    return r

# Mensajes masivos
def get_masiv():
    try:
        r = urlfetch.get(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/m-masivos?pk=" + str(bot.BOT_PK), validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error obteniendo masivo")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.STATE = "ERROR"
        bot.RESPONDE = bot.MASIVO = bot.AUTO = "NO"

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API get_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("Response: " + str(r.content))

        content = json.loads(r.content)
        r = content[0]
    else:
        r = {}

    return r

async def post_masiv(pk, estado):
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        fields = {}
        fields["pk"] = bot.BOT_PK
        fields["pk_mensaje"] = pk
        fields["estado"] = estado
        data = urllib.parse.urlencode(fields)
        
        r = urlfetch.post(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/m-masivos", validate_certificate=False, headers=headers, data=data)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error confirmando masivo")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.STATE = "ERROR"
        bot.RESPONDE = bot.MASIVO = bot.AUTO = "NO"

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API post_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("     pk_mensaje=" + str(pk))
            print("     estado=" + str(estado))
            print("Response: " + str(r.content))

        content = json.loads(r.content)
        r = content[0]
    else:
        r = {}

    return r

# Mensajes entrantes
async def send_inbounds(messages):
    try:
        for m in messages:
            fields = {
                "pk": bot.BOT_PK,
                "celular": m["celular"],
                "mensaje": m["mensaje"]
            }
            files = {}
            if m["archivo"] != "":
                files = {
                    "archivo": open(m["archivo"], "rb")
                }
            
            try:
                r = urlfetch.post(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/recepcion", validate_certificate=False, data=fields, files=files)
                # Buscar respuesta automática
                get_auto_response(mensaje=m["mensaje"], celular=m["celular"])
            except Exception as e:
                if bot.SHOW_ERRORS:
                    print(e)
                r = e
            time.sleep(0.5)
        
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error registrando entrante")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.STATE = "ERROR"
        bot.RESPONDE = bot.MASIVO = bot.AUTO = "NO"

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API post_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("     mensajes:")
            print(messages)
            print("Response: " + str(r.content))

        content = json.loads(r.content)
        r = content[0]
    else:
        r = {}

    return r
