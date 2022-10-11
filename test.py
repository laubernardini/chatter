from websocket import create_connection
import time

ws = create_connection("ws://localhost:8000/bots/apicloud/")
print(ws.recv())
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
time.sleep(30)
#ws.close()