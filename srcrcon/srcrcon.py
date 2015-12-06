import socket
import struct
import logging
LOG = logging.getLogger(__name__)

from tornado.ioloop import IOLoop

from srcrcon.connection import authenticate
from srcrcon.command import execute, Command


class SrcRCON:

    conn = None

    def __init__(self, host, port, password='') -> None:
        self.host = host
        self.port = port
        self.password = password

    async def send_command(self, cmd=None):
        pass

    def send_single_command(self, cmd):
        IOLoop.current().run_sync(lambda: self._single_command(cmd))

    async def _single_command(self, cmd):
        conn = await authenticate(self.password, host=self.host, port=self.port)
        cmd = Command(cmd)
        await execute(cmd, conn)
        conn.disconnect()
