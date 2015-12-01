"""
"""

import random
import struct


# Used internally to store packets (classes) that can be sent back by the server.
_registry = dict()

# Packet Types
#  3 - SERVERDATA_AUTH
#  2 - SERVERDATA_AUTH_RESPONSE
#  2 - SERVERDATA_EXECCOMMAND
#  0 - SERVERDATA_RESPONSE_VALUE

# Packet Structure
#  Size - 4 bytes
#  Id - 4 bytes
#  Type - 4 bytes
#  Body - ? bytes
#  NUL
#  NUL


class PacketMeta(type):

    _unpack_format = '<ii{body_len}s'

    def __call__(cls, *args, raw: bytes = None, **kwargs):
        id_ = body = None
        if raw:
            # subtracting 10 to account for the first 8 bytes (`id`, `type`) and
            # the trailing NULs
            body_len = len(raw) - 10
            id_, type_, body = struct.unpack(
                PacketMeta._unpack_format.format(body_len=body_len),
                raw[:-2]
            )
            cls = _registry[type_]

        obj = cls.__new__(cls, *args, **kwargs)
        obj.__init__(*args, **kwargs)

        obj.id = id_ or random.randint(1, 1000)
        obj.body = body or cls.body

        return obj


class Packet(metaclass=PacketMeta):
    """
    """
    _pack_format = '<iii{body_len}sxx'
    id = None
    type = None
    body = chr(0x00)

    @property
    def body_len(self) -> int:
        return self.body and len(self.body) or 0

    @property
    def size(self) -> int:
        return struct.calcsize(self._pack_format.format(body_len=self.body_len)) - 4

    def __bytes__(self):
        if self.type is None:
            raise AttributeError('Missing `type`')
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

    def __init__(self, password: str):
        self.body = password


class ServerDataAuthResponse(Packet):
    """
    """
    type = 2
_registry[ServerDataAuthResponse.type] = ServerDataAuthResponse


class ServerDataExecCommand(Packet):
    """
    """
    type = 2


class ServerDataResponseValue(Packet):
    """
    """
    type = 0
_registry[ServerDataResponseValue.type] = ServerDataResponseValue
