import base64
import msgpack

def decode_base64_msgpack_stream(b64_string):
    """
    Décode une chaîne Base64 contenant un ou plusieurs objets MessagePack.
    Retourne une liste d'objets Python.
    """
    raw_bytes = base64.b64decode(b64_string)

    unpacker = msgpack.Unpacker(raw=False)
    unpacker.feed(raw_bytes)

    objects = []
    for obj in unpacker:
        objects.append(obj)

    return objects


if __name__ == "__main__":
    # path_name = input("[?] Filename: ")
    # ws_file = open(path_name).read().splitlines()
    # for line in ws_file:
    #     decoded_objects = decode_base64_msgpack_stream(line)
    #     print(decoded_objects[0])
    while True: 
        b64_msgpack = input("")

        decoded_objects = decode_base64_msgpack_stream(b64_msgpack)
        print(decoded_objects)

