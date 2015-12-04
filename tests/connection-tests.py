import unittest.mock as mock

from tornado import netutil
from tornado.iostream import IOStream
from tornado.testing import AsyncTestCase, bind_unused_port, gen_test

from srcrcon.connection import Connection
from srcrcon.protocol import Auth, AuthResponse


class ConnectionMixin:
    conn = None

    def setUp(self):
        super(ConnectionMixin, self).setUp()
        self.conn = Connection()


class ListenerMixin:

    listener = None
    port = None

    def make_listener(self):
        self.listener, self.port = bind_unused_port()
        netutil.add_accept_handler(self.listener, self._on_connected)

    def _on_connected(self, connection, address):
        self.listener = IOStream(connection)


class ListenerConnectionMixin(ListenerMixin, ConnectionMixin):
    pass


class ConnectionConnectTests(ListenerConnectionMixin, AsyncTestCase):
    """Connection.connect()"""

    connected = False

    @gen_test
    def test_should_connect(self):
        self.make_listener()
        yield self.conn.connect('127.0.0.1', self.port)
        self.assertTrue(self.connected, "Didn't connect!")

    def _on_connected(self, connection, address):
        self.connected = True


class ConnectionSendTests(ListenerConnectionMixin, AsyncTestCase):
    """Connection.send()"""

    @gen_test
    def test_sends_data(self):
        self.make_listener()
        yield self.conn.connect('127.0.0.1', self.port)

        auth = Auth('me')
        yield self.conn.send(auth)
        data = yield self.listener.read_bytes(1024, partial=True)

        self.assertEquals(bytes(auth), data)


class ConnectionReadTests(ListenerConnectionMixin, AsyncTestCase):
    """Connection.read()"""

    @gen_test
    def test_reads_data(self):
        self.make_listener()
        yield self.conn.connect('127.0.0.1', self.port)

        auth_response = AuthResponse()
        yield self.listener.write(bytes(auth_response))
        data = yield self.conn.read()

        self.assertEquals(auth_response, data)
