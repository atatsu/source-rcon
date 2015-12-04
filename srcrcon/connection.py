import socket
import struct
import logging
LOG = logging.getLogger(__name__)
from typing import Union, Tuple

from tornado import iostream

from srcrcon.protocol import Packet


class Connection:

    host = None
    port = None
    socket = None
    stream = None

    _buffer = b''

    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream = iostream.IOStream(self.socket)

    async def connect(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

        await self.stream.connect((self.host,  self.port))
        LOG.info('Successfully connected to (%s, %s)', self.host, self.port)
        self.stream.set_close_callback(self.on_close)

    def disconnect(self) -> None:
        self.stream.close()
        LOG.info('Disconnected')

    async def send(self, packet: Packet) -> None:
        await self.stream.write(bytes(packet))
        LOG.debug('wrote %s', packet)

    async def read(self) -> Packet:
        self._buffer += await self.stream.read_bytes(1024, partial=True)
        packet, self._buffer = self._get_packet(self._buffer)
        return packet

    def on_close(self) -> None:
        LOG.info('Connection closed')

    def _get_packet(self, data: bytes) -> Union[Tuple[None, bytes], Tuple[Packet, bytes]]:
        if not data or len(data) < 4:
            return (None, data)

        size = struct.unpack('<i', data[:4])[0]
        if len(data[4:]) < size:
            return (None, data)

        packet = Packet(raw=data[4:size+4])
        return (packet, data[size+4:])
