import os

# Datos del bot
BOT_PK = "1"
THREAD = ""#"1"
STATE = "INICIANDO"
RESPONDE = "NO"
MASIVO = "NO"
AUTO = "NO"
READ = "NO"
PHONE = ""
VERSION = "2.0"

# Datos del server
SERVER_URL = "https://apicloud.com.ar/thread-"#"http://dev.apicloud.com.ar"#"http://localhost/thread-"#
FILE_SERVER = "https://apicloud.com.ar"#"http://dev.apicloud.com.ar"#"http://localhost:8000"#
FILE_SERVER_2 = "http://apicloud.com.ar:8080"#"http://localhost:8000"#

# Variables de ejecución
OS_SLASH = "\\" # / -> linux \\ -> windows
BROWSER = "chrome"
DOWNLOAD_PATH = os.getcwd() + OS_SLASH + 'inbound_file_cache' + OS_SLASH
DRIVER_PATH = "chromedriver.exe"#"/usr/local/bin/chromedriver"#
FIREFOX_DRIVER_PATH = "geckodriver.exe"
MIME_TYPES = "" # Los tipos incluidos se descargarán sin confirmación
MULTIMEDIA_EXT = ['.png', '.jpg', '.gif', '.jpeg', '.mp4', '.3gpp', '.quicktime', '.mp3', '.ogg', '.m4a'] # Estos archivos se envían por el botón "galería"
AUDIO_EXT = ['.3gpp', '.mp3', '.ogg', '.m4a']
START_DATE = None
FORCED_ACTIVITY_FREQUENCY = 240 # En minutos. Click para marcar al navegador como "activo" frente al SO 
CALL_RESPONSE = "*IMPORTANTE*\nEn este número *no recibimos llamadas*. Si así lo prefiere, puede redactar o enviarnos un mensaje de audio.\nDisculpe las molestias, muchas gracias."
REGISTERED_PHONE = ""
INVALID_PHONE_MESSAGE = '''
======================================================
¡EL NÚMERO SUMINISTRADO NO COINCIDE CON EL REGISTRADO!
======================================================
'''
INVALID_REGISTERED_PHONE_MESSAGE = '''
===================================
¡EL BOT NO TIENE NÚMERO REGISTRADO!
===================================
'''

# Log
SHOW_ERRORS = True
SHOW_API_RESPONSES = True
SHOW_EX_PRINTS = True

# Cache
FILE_CACHE = []
FILE_COUNTER = 0
CURRENT_CHAT = {}
LAST_MSG_CACHE = ""
AUTO_RESPONSES = []
NEXT_FORCED_ACTIVITY = None
CHATS = []
SLEEP_TIME = 0
CLIPBOARD_SLEEP_TIME = 0

# Funciones
def set_config(responde = "NO", masivo = "NO", auto = "NO", read="NO", thread = "1", registered_phone=""):
    global RESPONDE, MASIVO, AUTO, READ, THREAD, REGISTERED_PHONE
    
    RESPONDE = responde
    MASIVO = masivo
    AUTO = auto
    READ = read
    THREAD = thread
    REGISTERED_PHONE = registered_phone
    
def set_error():
    global STATE, THREAD, REGISTERED_PHONE

    STATE = 'ERROR'
    set_config(thread=THREAD, registered_phone=REGISTERED_PHONE)

