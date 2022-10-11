# Packages
import os, urlfetch, urllib, json, time

# Application
import bot

# Prints
def print_api_response(content, name="", data=None, status_code=None):
    data_text = ""
    if data:
        data_text = "Data:"
        for key, value in data.items():
            data_text += f"\n    {key}={value}"

    print(f'''\nAPI {name} status: {status_code}\n{data_text}\nResponse: {content}''')

def print_api_status_error(where="", status_code=None, exception=None, detail=None):
    exception_text = ""
    status_code_text = ""

    if exception:
        exception_text = f'''Exception:
        {exception}
        {repr(exception)}
        {exception.args}
        '''
    if status_code:
        status_code_text = f'''Detalle:
        La petición tuvo un estado distinto a 200: {status_code}
        '''

    print(f'''Error {where}:\n{status_code_text}\n{exception_text}\n{f'Detalle: {detail}' if detail else ""}\n''')

# Reporte
def status():
    print("Reportandose...")
    done = None
    while not done:
        try:
            r = urlfetch.get(f'{bot.SERVER_URL}{bot.THREAD}/api/bots/report?pk={bot.BOT_PK}&estado={bot.STATE}', validate_certificate=False, timeout=3)
            print(f'request_time {r.total_time}')
            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="report", data={"pk": bot.BOT_PK, "estado": bot.STATE}, status_code=r.status_code)

            if r.status_code == 200:
                content = json.loads(r.content)
                content = content[0]

                bot.set_config(responde = content["responde"], masivo = content["masivo"], read= content["read"], auto = content["auto"], thread = content["thread"], registered_phone = content["phone"])
                
                done = True
                print("Reporte completo")
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="en reporte", status_code=r.status_code)
                bot.set_error()
                time.sleep(3)
                print("Reintentando...")
        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="en reporte", exception=e)
            bot.set_error()
            time.sleep(3)
            print("Reintentando...")

# Obtener último mensaje del chat
def get_last_msg(celular):
    print("Buscando último mensaje en DB...")

    result = None
    done = None
    while not done:
        try:
            r = urlfetch.get(f'{bot.SERVER_URL}{bot.THREAD}/api/bots/get-last-msg?token={bot.BOT_PK}&celular={celular}', validate_certificate=False, timeout=5)
            print(f'request_time {r.total_time}')

            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="get_chats", data={"pk": bot.BOT_PK}, status_code=r.status_code)
            
            if r.status_code == 200:
                content = json.loads(r.content)
                if content["request_status"] == 'success':
                    if content["detail"]:
                        result = content["detail"]

                    done = True
                    print(f"Mensaje obtenido: {result}")
                else:
                    if bot.SHOW_ERRORS:
                        print_api_status_error(where="obteniendo último mensaje", detail=content["detail"])
                    bot.set_error()
                    time.sleep(3)
                    print("Reintentando...")
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="obteniendo último mensaje", status_code=r.status_code)
                bot.set_error()
                time.sleep(3)
                print("Reintentando...")
        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="obteniendo último mensaje", exception=e)
            bot.set_error()    
            time.sleep(3)
            print("Reintentando...")    

    return result

# Obtener archivo
def get_file(url):
    if bot.SHOW_EX_PRINTS:
        print("Obteniendo archivo...")
    
    s = bot.FILE_SERVER
    done = None
    while not done:
        try:
            if bot.SHOW_EX_PRINTS:
                print("Intentando con " + s + url)
            
            r = urlfetch.get(f'{s}{url}', validate_certificate=False, timeout=30)
            print(f'request_time {r.total_time}')

            if r.status_code == 200:
                done = True
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="obteniendo archivo", status_code=r.status_code)
                
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
                print_api_status_error(where="obteniendo archivo", exception=e)
            
            time.sleep(2)
    
    filename = url.rsplit('/', 1)[1]
    if not os.path.exists("file_cache" + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH):
        os.makedirs("file_cache" + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH)
    
    open("file_cache" + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH + filename, "wb").write(r.content)

    return os.path.abspath("file_cache" + bot.OS_SLASH + str(bot.BOT_PK) + bot.OS_SLASH + filename)

# Respuestas manuales
def get_response():
    print("Buscando respuestas manuales...")
    done = None
    result = {}
    while not done:
        try:
            r = urlfetch.get(f'{bot.SERVER_URL}{bot.THREAD}/api/bots/respuesta?token={bot.BOT_PK}', validate_certificate=False, timeout=6)
            print(f'request_time {r.total_time}')

            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="get_response", data={"pk": bot.BOT_PK}, status_code=r.status_code)
            
            if r.status_code == 200:
                content = json.loads(r.content)
                if content["request_status"] == 'success':
                    result = content["detail"]
                
                done = True
                print(f"Respuesta manual obtenida: {result}")
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="obteniendo respuesta manual", status_code=r.status_code)
                bot.set_error()
                print("Reintentando...")
                time.sleep(3)
        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="obteniendo respuesta manual", exception=e)
            bot.set_error()
            print("Reintentando...")
            time.sleep(3)

    return result

def post_response(pk, estado, wa_id):
    print("Confirmando respuesta manual...")

    # Data
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    fields = {
        "token": bot.BOT_PK,
        "pk": pk,
        "estado": estado,
        "wa_id": wa_id
    }
    data = urllib.parse.urlencode(fields)

    done = None
    while not done:
        try:
            r = urlfetch.post(f'{bot.SERVER_URL}{bot.THREAD}/api/bots/respuesta', validate_certificate=False, headers=headers, data=data, timeout=8)
            print(f'request_time {r.total_time}')

            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="post_response", data=fields, status_code=r.status_code)

            if r.status_code == 200:
                done = True
                print("Respuesta manual confirmada")            
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="enviando respuesta", status_code=r.status_code)
                bot.set_error()
                print("Reintentando...")
                time.sleep(3)
        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="enviando respuesta", exception=e)
            bot.set_error()
            print("Reintentando...")
            time.sleep(3)

# Respuestas automáticas
def post_auto_response(pk, contacto_id, wa_id, tipo, mensaje, celular):
    print("Confirmando respuesta automática...")

    # Data
    fields = {
        "token": bot.BOT_PK,
        "pk": pk,
        "contacto_id": contacto_id,
        "wa_id": wa_id,
        "tipo": tipo,
        "mensaje": mensaje,
        "celular": celular
    }

    done = None
    while not done:
        try:
            r = urlfetch.post(f'{bot.SERVER_URL}{bot.THREAD}/api/bots/r-auto', data=fields, validate_certificate=False, timeout=8)
            print(f'request_time {r.total_time}')

            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="post_auto_response", data=fields, status_code=r.status_code)
            
            if r.status_code == 200:
                done = True
                print("Respuesta automática confirmada")            
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="confirmando respuesta automática", status_code=r.status_code)
                bot.set_error()
                print("Reintentando...")
                time.sleep(3)

        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="confirmando respuesta automática", exception=e)
            bot.set_error()
            print("Reintentando...")
            time.sleep(3)

# Mensajes masivos
def get_masiv():
    print("Buscando mensaje masivo")

    result = {}
    done = None
    while not done:
        try:
            r = urlfetch.get(f'{bot.SERVER_URL}{bot.THREAD}/api/bots/m-masivos?token={bot.BOT_PK}', validate_certificate=False, timeout=6)
            print(f'request_time {r.total_time}')

            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="get_masiv", data={"pk": bot.BOT_PK}, status_code=r.status_code)

            if r.status_code == 200:
                content = json.loads(r.content)
                if content["request_status"] == 'success':
                    result = content["detail"]
                
                done = True
                print(f"Mensaje masivo obtenido: {result}")
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="obteniendo mensaje masivo", status_code=r.status_code)
                bot.set_error()
                print("Reintentando...")
                time.sleep(3)
        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="obteniendo mensaje masivo", exception=e)
            bot.set_error()
            print("Reintentando...")
            time.sleep(3)

    return result

def post_masiv(pk, estado, wa_id, intentos, errores):    
    print("Confirmando mensaje masivo")

    # Data
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

    done = None
    while not done:
        try:
            r = urlfetch.post(f'{bot.SERVER_URL}{bot.THREAD}/api/bots/m-masivos', validate_certificate=False, headers=headers, data=data, timeout=8)
            print(f'request_time {r.total_time}')

            if bot.SHOW_API_RESPONSES:
                print_api_response(content=r.content, name="post_masiv", data=fields, status_code=r.status_code)

            if r.status_code == 200:
                done = True
                print("Mensaje masivo confirmado")
            else:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="confirmando mensaje masivo", status_code=r.status_code)
                bot.set_error()
                print("Reintentando...")
                time.sleep(3)
        except Exception as e:
            if bot.SHOW_ERRORS:
                print_api_status_error(where="confirmando mensaje masivo", exception=e)
            bot.set_error()
            print("Reintentando...")
            time.sleep(3)

# Mensajes entrantes
def send_inbounds(messages):
    print("Subiendo mensajes entrantes...")
    
    cant = len(messages)
    count = 1
    for m in messages:
        print(f"Subiendo: {count}/{cant}")
        timeout = 8
        files = {}
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
        if m["archivo"] != "":
            timeout = 15
            files = {
                "archivo": open(m["archivo"], "rb")
            }
        
        done = None
        while not done:
            try:
                r = urlfetch.post(f'{bot.SERVER_URL}{bot.THREAD}/api/bots/recepcion', validate_certificate=False, data=fields, files=files, timeout = timeout)
                print(f'request_time {r.total_time}')

                if bot.SHOW_API_RESPONSES:
                    print_api_response(content=r.content, name="send_inbound", data={"pk": bot.BOT_PK, "mensajes": messages}, status_code=r.status_code)

                # Guardar respuesta automática
                if r.status_code == 200:
                    content = json.loads(r.content)
                    if content["request_status"] == 'success':
                        if content["detail"]:
                            bot.AUTO_RESPONSES.append(content['detail'])

                        done = True
                        print("Entrante subido")
                    else:
                        if bot.SHOW_ERRORS:
                            print_api_status_error(where="registrando entrante", detail=content["detail"])
                            bot.set_error()
                            print("Reintentando...")
                            time.sleep(3)
                else:
                    if bot.SHOW_ERRORS:
                        print_api_status_error(where="registrando entrante", status_code=r.status_code)
                    bot.set_error()
                    print("Reintentando...")
                    time.sleep(3)
            except Exception as e:
                if bot.SHOW_ERRORS:
                    print_api_status_error(where="registrando entrante", exception=e)
                bot.set_error()
                print("Reintentando...")
                time.sleep(3)

        time.sleep(0.25)
        count += 1
