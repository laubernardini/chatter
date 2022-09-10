# Packages
import os, urlfetch, urllib, json, asyncio, time

# Application
import bot

# Reporte
def status():
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
        bot.set_error()

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API status: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("     estado=" + str(bot.STATE))
            print("Response: " + str(r.content))

        if r.status_code == 200:
            content = json.loads(r.content)
            content = content[0]

            bot.set_config(responde = content["responde"], masivo = content["masivo"], auto = content["auto"], thread = content["thread"], registered_phone = content["phone"])
        else:
            if bot.SHOW_ERRORS:
                print("Error enviando estado")
                print("  Detalle: ")
                print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))

            bot.set_error()

def get_last_msg(celular):
    try:
        r = urlfetch.get(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/get-last-msg?token=" + str(bot.BOT_PK) + "&celular=" + str(celular), validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error obteniendo chats")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        
        r = e
        bot.set_error()

    result = None
    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API get_chats: " + str(r.status_code))
            print("Data:")
            print("     token=" + str(bot.BOT_PK))
            print("Response: " + str(r.content))
        
        if r.status_code == 200:
            content = json.loads(r.content)
            if content["request_status"] == 'success':
                if content["detail"]:
                    result = content["detail"]
            else:
                r = ""
                if bot.SHOW_ERRORS:
                    print("Error obteniendo chats")
                    print("  Detalle: ")
                    print("    " + str(content["detail"]))

                    bot.set_error()
            
        else:
            if bot.SHOW_ERRORS:
                print("Error obteniendo chats")
                print("  Detalle: ")
                print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
            
            bot.set_error()

    return result

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

            if r.status_code == 200:
                done = True
            else:
                if bot.SHOW_ERRORS:
                    print("Error obteniendo archivo")
                    print("  Detalle: ")
                    print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
                
                if s == bot.FILE_SERVER:
                    s = bot.FILE_SERVER_2
                else:
                    s = bot.FILE_SERVER
                time.sleep(2)
            
        except Exception as e:
            if s == bot.FILE_SERVER:
                s = bot.FILE_SERVER_2
            else:
                s = bot.FILE_SERVER

            if bot.SHOW_ERRORS:
                print(e)
            
            time.sleep(2)
    
    filename = url.rsplit('/', 1)[1]
    if not os.path.exists("file_cache" + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH):
        os.makedirs("file_cache" + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH)
    
    open("file_cache" + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH + filename, "wb").write(r.content)

    return os.path.abspath("file_cache" + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH + filename)

# Respuestas manuales
def get_response():
    try:
        r = urlfetch.get(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/respuesta?token=" + str(bot.BOT_PK), validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error obteniendo respuesta")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        
        r = e
        bot.set_error()

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API get_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("Response: " + str(r.content))
        
        if r.status_code == 200:
            content = json.loads(r.content)
            if content["request_status"] == 'success':
                r = content["detail"]
            else:
                r = {}

        else:
            if bot.SHOW_ERRORS:
                print("Error obteniendo respuesta")
                print("  Detalle: ")
                print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
            
            bot.set_error()
            r = {}
    else:
        r = {}

    return r

async def post_response(pk, estado, wa_id):
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        fields = {}
        fields["token"] = bot.BOT_PK
        fields["pk"] = pk
        fields["estado"] = estado
        fields["wa_id"] = wa_id
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
        bot.set_error()

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API post_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("     pk_respuesta=" + str(pk))
            print("Response: " + str(r.content))

        if r.status_code != 200:
            if bot.SHOW_ERRORS:
                print("Error confirmando respuesta")
                print("  Detalle: ")
                print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
            
            bot.set_error()

# Respuestas automáticas
async def post_auto_response(pk, celular, wa_id, tipo, mensaje=None):
    try:
        files = {}
        fields = {
            "token": bot.BOT_PK,
            "pk": pk,
            "celular": celular,
            "wa_id": wa_id,
            "tipo": tipo,
            "mensaje": mensaje
        }
        r = urlfetch.post(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/r-auto", data=fields, validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error confirmando respuesta automática")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        
        r = e
        bot.set_error()

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API post_auto_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("Response: " + str(r.content))
        
        if r.status_code != 200:
            if bot.SHOW_ERRORS:
                print("Error confirmando respuesta automática")
                print("  Detalle: ")
                print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
            
            bot.set_error()

# Mensajes masivos
def get_masiv():
    try:
        r = urlfetch.get(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/m-masivos?token=" + str(bot.BOT_PK), validate_certificate=False)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error obteniendo masivo")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.set_error()

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API get_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("Response: " + str(r.content))

        if r.status_code == 200:
            content = json.loads(r.content)
            if content["request_status"] == 'success':
                r = content["detail"]
            else:
                r = {}
        else:
            if bot.SHOW_ERRORS:
                print("Error obteniendo mensaje masivo")
                print("  Detalle: ")
                print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
            
            bot.set_error()
            r = {}
    else:
        r = {}

    return r

async def post_masiv(pk, estado, wa_id, intentos, errores):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        fields = {
            "token": bot.BOT_PK,
            "pk": pk,
            "estado": estado,
            "wa_id": wa_id,
            "intentos": intentos,
            "errores": errores
        }
        data = json.dumps(fields)
        
        r = urlfetch.post(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/m-masivos", validate_certificate=False, headers=headers, data=data)
    except Exception as e:
        if bot.SHOW_ERRORS:
            print("Error confirmando masivo")
            print("     Detalle: ")
            print(e)
            print(repr(e))
            print(e.args)
        r = e
        bot.set_error()

    if type(r) != urlfetch.UrlfetchException:
        if bot.SHOW_API_RESPONSES:
            print("API post_response: " + str(r.status_code))
            print("Data:")
            print("     pk=" + str(bot.BOT_PK))
            print("     pk_mensaje=" + str(pk))
            print("     estado=" + str(estado))
            print("Response: " + str(r.content))

        if r.status_code != 200:
            if bot.SHOW_ERRORS:
                print("Error confirmando masivo")
                print("  Detalle: ")
                print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
            
            bot.set_error()

# Mensajes entrantes
async def send_inbounds(messages):
    for m in messages:
        fields = {
            "token": bot.BOT_PK,
            "celular": m["celular"],
            "nombre": m["nombre"],
            "mensaje": m["mensaje"],
            "wa_id": m["wa_id"],
        }

        if m["respuesta"] != {}:
            fields["respuesta_grupo"] = m["respuesta"]["grupo"],
            fields["respuesta_mensaje"] = m["respuesta"]["mensaje"]

        files = {}
        if m["archivo"] != "":
            files = {
                "archivo": open(m["archivo"], "rb")
            }
        
        try:
            r = urlfetch.post(str(bot.SERVER_URL) + str(bot.THREAD) + "/api/bots/recepcion", validate_certificate=False, data=fields, files=files)

            # Guardar respuesta automática
            if r.status_code == 200:
                content = json.loads(r.content)
                if content["request_status"] == 'success':
                    if content["detail"]:
                        bot.AUTO_RESPONSES.append(content['detail'])
                else:
                    if bot.SHOW_ERRORS:
                        print("Error registrando entrante")
                        print("  Detalle: ")
                        print("    " + str(content["detail"]))

                        bot.set_error()
                        r = {}
            else:
                if bot.SHOW_ERRORS:
                    print("Error registrando entrante")
                    print("  Detalle: ")
                    print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))
                
                bot.set_error()
                r = {}
        except Exception as e:
            if bot.SHOW_ERRORS:
                print("Error registrando entrante")
                print("     Detalle: ")
                print(e)
                print(repr(e))
                print(e.args)
            
            r = e
            bot.set_error()
        
        if type(r) != urlfetch.UrlfetchException:
            if bot.SHOW_API_RESPONSES:
                print("API post_response: " + str(r.status_code))
                print("Data:")
                print("     pk=" + str(bot.BOT_PK))
                print("     mensajes:")
                print(messages)
                print("Response: " + str(r.content))
            
            if r.status_code != 200:
                if bot.SHOW_ERRORS:
                    print("Error registrando entrante")
                    print("  Detalle: ")
                    print("    La petición tuvo un estado distinto a 200: " + str(r.status_code))

                bot.set_error()

        time.sleep(0.25)
