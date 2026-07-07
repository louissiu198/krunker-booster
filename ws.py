import msgpack

class ws:
    @staticmethod
    def encode_msgpack(data: list) -> bytes:
        pck = b''
        for msg in data:
            pck += msgpack.packb(msg)
        return pck 

    @staticmethod
    def decode_msgpack_stream(data: bytes):
        try:
            unpacker = msgpack.Unpacker(raw=False)
            unpacker.feed(data)
            objects = []
            for obj in unpacker:
                objects.append(obj)
            return objects
        except Exception as e:
            return None
