from websocket import create_connection
import json


src = {
    'mode': 'tako',
    'data': {
        'name': 'seki',
        'age': 18,
    }
}

wc = create_connection('ws://0.0.0.0:9999/')
wc.send(json.dumps(src))

with create_connection('ws://0.0.0.0:9999/') as wc:
    wc.send(json.dumps(src))
