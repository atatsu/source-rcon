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
        # if data came in and had a body take that, if not and the subclass has a body
        # take that, lastly take the base class's body if necessary
        obj.body = body.decode('utf-8') if raw is not None else obj.body or cls._body

        return obj


class Packet(metaclass=PacketMeta):
    """
    Base packet. Also used to create instances of the various subclasses from data
    received from the server.
    """
    _pack_format = '<iii{body_len}sxx'
    id = None
    type = None
    _body = ''

    @property
    def body(self) -> str:
        return self._body

    @body.setter
    def body(self, value: str):
        self._body = value

    def __repr__(self) -> str:
        return '{name}(size={size:d}, id={id:d}, type={type:d}, body={body!r})'.format(
            name=self.__class__.__name__,
            size=len(self),
            id=self.id,
            type=self.type,
            body=self.body
        )

    def __bytes__(self) -> bytes:
        if self.type is None:
            raise AttributeError('Missing `type`')
        return struct.pack(
            self._pack_format.format(body_len=len(self.body)),
            len(self),
            self.id,
            self.type,
            bytes(self.body, 'ascii'),
        )

    def __len__(self) -> int:
        return struct.calcsize(
            self._pack_format.format(body_len=len(self.body))
        ) - 4

    def __eq__(self, other) -> bool:
        return (isinstance(other, Packet) and
            self.id == other.id and
            self.type == other.type and
            self.body == other.body)


class AuthPacket(Packet):
    """
    Used to authenticate the connection with the server.
    """
    type = 3

    def __init__(self, password: str) -> None:
        self.body = password


class AuthResponsePacket(Packet):
    """
    Sent in response to an `AuthPacket` packet and contains the connection's current
    auth status.
    """
    type = 2
_registry[AuthResponsePacket.type] = AuthResponsePacket


class ExecCommandPacket(Packet):
    """
    Used to issue commands to the server.
    """
    type = 2


class ResponseValuePacket(Packet):
    """
    Sent in response to an `ExecCommand` packet.
    """
    type = 0
_registry[ResponseValuePacket.type] = ResponseValuePacket
