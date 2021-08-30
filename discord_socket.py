import os
from dotenv import load_dotenv

import json
import websocket

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

heartbeat = {
    "op": 1,
    "d": 1
}

id_message = {
    "op": 2,
    "d": {
        "token": TOKEN,
        "intents": 513,
        "properties": {
            "$os": "linux",
            "$browser": "my_library",
            "$device": "my_library"
        }
    }
}

websocket.enableTrace(True)
# ws = websocket.WebSocketApp("wss://gateway.discord.gg",
#                           on_open=on_open,
#                           on_message=on_message,
#                           on_error=on_error,
#                           on_close=on_close)
# ws.run_forever()
ws = websocket.WebSocket()
ws.connect("wss://gateway.discord.gg")

data = json.dumps(id_message)
ws.send(data)
result = ws.recv()
print(result)

while True:
    data = json.dumps(heartbeat)
    ws.send(data)
    result = ws.recv()
    result = json.loads(result)
    if result["op"] != 11 and result["op"] != 1:
        print(result)
