import unittest

from tornado.testing import AsyncTestCase, gen_test

from testing import ListenerConnectionMixin

from srcrcon.protocol import Auth, AuthResponse


class ConnectionConnectTests(ListenerConnectionMixin, AsyncTestCase):
    """Connection.connect()"""

    connected = False

    @gen_test
    def test_should_connect(self):
        yield self.conn.connect()
        self.assertTrue(self.connected, "Didn't connect!")

    def _on_connected(self, connection, address):
        self.connected = True


class ConnectionSendTests(ListenerConnectionMixin, AsyncTestCase):
    """Connection.send()"""

    @gen_test
    def test_sends_data(self):
        yield self.make_listener_and_connect()

        auth = Auth('me')
        yield self.conn.send(auth)
        data = yield self.listener.read_bytes(1024, partial=True)

        self.assertEquals(bytes(auth), data)


class ConnectionReadTests(ListenerConnectionMixin, AsyncTestCase):
    """Connection.read()"""

    @gen_test
    def test_reads_data(self):
        yield self.make_listener_and_connect()

        auth_response = AuthResponse()
        yield self.listener.write(bytes(auth_response))
        data = yield self.conn.read()

        self.assertEquals(auth_response, data)
