import json
import base64
import random
import msgpack

ws_json = input("[?] Json file name: ")
with open(f'{ws_json}.json', 'r') as file:
    json_data = json.load(file)

def decode_base64_msgpack_stream(b64_string):
    raw_bytes = base64.b64decode(b64_string)

    unpacker = msgpack.Unpacker(raw=False)
    unpacker.feed(raw_bytes)

    objects = []
    for obj in unpacker:
        objects.append(obj)

    return objects

id = random.randint(100, 999)
data_values = []
for entry in json_data['log']['entries']:
    for ws_message in entry['_webSocketMessages']:
        if 'data' in ws_message:
            if ws_message["type"] == "send":
                data_values.append(ws_message['data'])
                decoded = decode_base64_msgpack_stream(ws_message['data'])[0]
                with open(f"old_log_{id}.txt", "a+") as f:
                    f.write(f"{decoded},\n")

print(f"Found {len(data_values)} data entries, saved as {id}")