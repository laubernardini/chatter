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
RELOAD_FRECUENCY = 5 # En minutos

# Log
SHOW_ERRORS = True
SHOW_API_RESPONSES = False
SHOW_EX_PRINTS = True

# Cache
LAST_FILE = ""
LAST_MSG_CACHE = ""
AUTO_RESPONSES = []
NEXT_RELOAD = None

