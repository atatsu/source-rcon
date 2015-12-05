import socket
import struct
import logging
LOG = logging.getLogger(__name__)
from typing import Union, Tuple, Optional

from tornado import iostream

from .protocol import Packet, AuthPacket, AuthResponsePacket
from .exceptions import AuthenticationFailure


class Connection:

    @property
    def open(self) -> bool:
        return not self._stream.closed()

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._buffer = b''
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._stream = iostream.IOStream(self._socket)

    async def connect(self) -> None:
        await self._stream.connect((self._host, self._port))
        LOG.info('Successfully connected to (%s, %s)', self._host, self._port)
        self._stream.set_close_callback(self.on_close)

    def disconnect(self) -> None:
        """Disconnect from the server."""
        self._stream.close()
        LOG.info('Disconnected')

    async def send(self, packet: Packet) -> None:
        """Sends a packet."""
        await self._stream.write(bytes(packet))
        LOG.debug('wrote %s', packet)

    async def read(self) -> Optional[Packet]:
        """Returns a packet if enough data was received."""
        buf = await self._stream.read_bytes(1024, partial=True)
        if not buf:
            return

        self._buffer += buf
        packet, self._buffer = self._get_packet(self._buffer)
        if packet:
            LOG.debug('read %s', packet)
        return packet

    def on_close(self) -> None:
        LOG.info('Connection closed')

    def _get_packet(self, data: bytes) -> Union[Tuple[None, bytes], Tuple[Packet, bytes]]:
        """
        Reads socket data and if enough data is present will construct a `Packet` instance
        from it, or else `None`. Either way the remaining buffer data is also returned.
        """
        if not data or len(data) < 4:
            return (None, data)

        size = struct.unpack('<i', data[:4])[0]
        if len(data[4:]) < size:
            return (None, data)

        packet = Packet(raw=data[4:size+4])
        return (packet, data[size+4:])


async def authenticate(
    password: str,
    conn: Connection = None,
    host: str = None,
    port: int = None
) -> Connection:
    """
    Authenticates a connection. Connection details can be supplied in place
    of an actual connection and a new one will be created.
    """
    if conn is None:
        LOG.debug('no connection supplied, creating new one')
        conn = Connection(host, port)
        await conn.connect()

    auth = AuthPacket(password)
    await conn.send(auth)
    packet = await conn.read()

    if packet and isinstance(packet, AuthResponsePacket) and packet.id == auth.id:
        # conn._authenticated = True
        LOG.info('Authentication successful')
        return conn

    LOG.error('Authentication failed')
    raise AuthenticationFailure
