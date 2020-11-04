import os

# Datos del bot
BOT_PK = "1"
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
DOWNLOAD_PATH = os.getcwd() + '\inbound_file_cache\\'
MIME_TYPES = ""
MULTIMEDIA_EXT = ['.png', '.jpg', '.gif', '.jpeg', '.mp4', '.3gpp', '.quicktime']
SHOW_ERRORS = True
SHOW_API_RESPONSES = False
SHOW_EX_PRINTS = False

# Cache
LAST_FILE = ""
LAST_MSG_CACHE = ""

