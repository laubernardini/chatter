# Datos del bot
PHONE = ""
VERSION = "1.0"

# Variables de ejecución
OS_SLASH = "\\" # / -> linux \\ -> windows
SERVER_URL = "https://apicloud.com.ar"#"http://localhost:8000"#
BROWSER = "chrome"
DRIVER_PATH = "chromedriver.exe"#"/usr/local/bin/chromedriver"#
BROWSER_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
FORCED_ACTIVITY_FREQUENCY = 5 # En minutos. Click para marcar al navegador como "activo" frente al SO 
START_DATE = None
NEXT_SEND = None
MODE_CHANGE = None
AWAIT_TIME = 5
MESSAGE = ""
DESCRIPCION = "-"
GROUPS_ONLY = False
START_MSG_CODE = "Hola! Soy chatter"
RESPONSE_MSG = "Ok, "
CHATTER_CODE = 'cttr'
GROUPS_LIST_SOURCE = 0
MODE_CHANGE_TIME = 20
MODE = "GROUPS"

# Log
SHOW_ERRORS = True
SHOW_API_RESPONSES = True
SHOW_EX_PRINTS = True

# Cache
NEXT_FORCED_ACTIVITY = None
SLEEP_TIME = 0
CLIPBOARD_SLEEP_TIME = 0
GROUPS_LIST = []
PHONES_LIST = []
LAST_SEND = None
ACTUAL_READED_MSG = ""
ACTUAL_READED_GROUP = ""

def calc_sleeptime():
    global PHONE, SLEEP_TIME, CLIPBOARD_SLEEP_TIME

    sleep_time = float(int(PHONE) / 10)
    while sleep_time > 3:
        sleep_time /= 2
    SLEEP_TIME = sleep_time
    CLIPBOARD_SLEEP_TIME = (sleep_time if sleep_time < 3 else sleep_time / 2) if (sleep_time > 1) else (sleep_time + 1)

def set_message():
    global PHONE, CHATTER_CODE, MESSAGE

    MESSAGE = f"Hola! Soy chatter _*{PHONE}*_ (_{CHATTER_CODE}_)"
