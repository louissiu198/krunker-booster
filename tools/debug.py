import base64
import msgpack

def decode_base64_msgpack_stream(b64_string):
    raw_bytes = base64.b64decode(b64_string)
    unpacker = msgpack.Unpacker(raw=False)
    unpacker.feed(raw_bytes)

    objects = []
    for obj in unpacker:
        objects.append(obj)

    return objects


if __name__ == "__main__":
    while True: 
        b64_msgpack = input("")

        decoded_objects = decode_base64_msgpack_stream(b64_msgpack)
        print(decoded_objects)

