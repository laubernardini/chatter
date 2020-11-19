import os

# Datos del bot
BOT_PK = "5"
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
RELOAD_FREQUENCY = 5 # En minutos
CALL_RESPONSE = "*IMPORTANTE*\nEn este número *no recibimos llamadas*. Si así lo prefiere, puede redactar o enviarnos un mensaje de audio.\nDisculpe las molestias, muchas gracias."


# Log
SHOW_ERRORS = True
SHOW_API_RESPONSES = False
SHOW_EX_PRINTS = False

# Cache
LAST_FILE = ""
LAST_MSG_CACHE = ""
AUTO_RESPONSES = []
NEXT_RELOAD = None

