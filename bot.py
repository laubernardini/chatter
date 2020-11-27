import os

# Datos del bot
BOT_PK = "9"
THREAD = "1"
STATE = "INICIANDO"
RESPONDE = "NO"
MASIVO = "NO"
AUTO = "NO"

# Datos del server
SERVER_URL = "https://apicloud.com.ar/thread-"
FILE_SERVER = "http://apicloud.com.ar:8080"
FILE_SERVER_2 = "https://apicloud.com.ar"

# Variables de ejecución
OS_SLASH = "/" # / -> linux \\ -> windows
DOWNLOAD_PATH = os.getcwd() + OS_SLASH + 'inbound_file_cache' + OS_SLASH
MIME_TYPES = "" # Los tipos incluidos se descargarán sin confirmación
MULTIMEDIA_EXT = ['.png', '.jpg', '.gif', '.jpeg', '.mp4', '.3gpp', '.quicktime'] # Estos archivos se envían por el botón "galería"
START_DATE = None
FORCED_ACTIVITY_FREQUENCY = 10 # En minutos. Click para marcar al navegador como "activo" frente al SO 
CALL_RESPONSE = "*IMPORTANTE*\nEn este número *no recibimos llamadas*. Si así lo prefiere, puede redactar o enviarnos un mensaje de audio.\nDisculpe las molestias, muchas gracias."


# Log
SHOW_ERRORS = True
SHOW_API_RESPONSES = True
SHOW_EX_PRINTS = True

# Cache
LAST_FILE = ""
LAST_MSG_CACHE = ""
AUTO_RESPONSES = []
NEXT_FORCED_ACTIVITY = None

# Funciones
def set_config(responde = "NO", masivo = "NO", auto = "NO", thread = "1"):
    RESPONDE = responde
    MASIVO = masivo
    AUTO = auto
    THREAD = thread

def set_error():
    STATE = 'ERROR'
    set_config(thread=THREAD)

