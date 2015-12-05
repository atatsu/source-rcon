from tornado import netutil
from tornado.iostream import IOStream
from tornado.testing import bind_unused_port

from srcrcon.connection import Connection


class ListenerMixin:

    listener = None
    port = None

    def make_listener(self):
        self.listener, self.port = bind_unused_port()
        netutil.add_accept_handler(self.listener, self._on_connected)

    def _on_connected(self, connection, address):
        self.listener = IOStream(connection)


class ConnectionMixin:
    conn = None

    def setUp(self):
        super(ConnectionMixin, self).setUp()
        self.make_listener()
        self.conn = Connection('127.0.0.1', self.port)


class ListenerConnectionMixin(ListenerMixin, ConnectionMixin):

    async def make_listener_and_connect(self):
        await self.conn.connect()
