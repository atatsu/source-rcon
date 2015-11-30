"""
"""

import random
import struct


class PacketMeta(type):

    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        obj.__init__(*args, **kwargs)

        obj.id = random.randint(1, 1000)

        return obj


# Packet Types
# 3 - SERVERDATA_AUTH
# 2 - SERVERDATA_AUTH_RESPONSE
# 2 - SERVERDATA_EXECCOMMAND
# 0 - SERVERDATA_RESPONSE_VALUE


class Packet(metaclass=PacketMeta):
    """
    """
    _size_format = '<i'
    _pack_format = '<iii{body_len}sxx'
    id = None
    type = None
    body = None

    def __new__(cls, payload=None, auth_response=False):
        return super(Packet, cls).__new__(cls)

    @property
    def body_len(self):
        return self.body and len(self.body) or 0

    @property
    def size(self):
        return struct.calcsize(self._pack_format.format(body_len=self.body_len)) - 4

    def __bytes__(self):
        return struct.pack(
            self._pack_format.format(body_len=self.body_len),
            self.size,
            self.id,
            self.type,
            bytes(self.body, 'ascii'),
        )


class ServerDataAuth(Packet):
    """
    """
    type = 3

    def __init__(self, password):
        self.body = password


class ServerDataAuthResponse(Packet):
    """
    """
    type = 2 

    def __init__(self, payload):
        pass


class ServerDataExecCommand(Packet):
    """
    """
    type = 2


class ServerDataResponseValue(Packet):
    """
    """
    type = 0
