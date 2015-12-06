import unittest
import unittest.mock as mock

from tornado.ioloop import TimeoutError
from tornado.gen import coroutine, sleep
from tornado.testing import AsyncTestCase, gen_test

from testing import ListenerConnectionMixin

from srcrcon.protocol import AuthPacket, AuthResponsePacket
from srcrcon.connection import authenticate, Connection
from srcrcon.exceptions import AuthenticationError


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

        auth = AuthPacket('me')
        yield self.conn.send(auth)
        data = yield self.listener.read_bytes(1024, partial=True)

        self.assertEquals(bytes(auth), data)


class ConnectionReadTests(ListenerConnectionMixin, AsyncTestCase):
    """Connection.read()"""

    @gen_test
    def test_reads_data(self):
        yield self.make_listener_and_connect()

        auth_response = AuthResponsePacket()
        yield self.listener.write(bytes(auth_response))
        data = yield self.conn.read()

        self.assertEquals(auth_response, data)

class AuthenticateSuccessTests(ListenerConnectionMixin, AsyncTestCase):

    def setUp(self):
        super(AuthenticateSuccessTests, self).setUp()
        self.password = 'mypassword'


    @mock.patch('random.randint')
    @gen_test
    def test_connection_returned(self, _randint):
        """return connection and be `authenticated` if server replies with same id"""
        _randint.return_value = 5

        yield self.make_listener_and_connect()

        conn, received_data = yield [
            authenticate(self.password, self.conn),
            self._listen_for_auth_request()
        ]

        auth_check = AuthPacket(self.password)
        self.assertEquals(bytes(auth_check), received_data, 'client sent non-auth request')
        self.assertEquals(self.conn, conn)

    @mock.patch('random.randint')
    @gen_test
    def test_with_conn_parms(self, _randint):
        """create a new connection if none supplied"""
        _randint.return_value = 5

        self.make_listener()

        auth_action = authenticate(self.password, host='127.0.0.1', port=self.port)
        listen_action = self._listen_for_auth_request()

        conn, received_data = yield [auth_action, listen_action]

        auth_check = AuthPacket(self.password)
        self.assertEquals(bytes(auth_check), received_data, 'client sent non-auth request')
        self.assertTrue(isinstance(conn, Connection))

    @coroutine
    def _listen_for_auth_request(self):
        # no `listener` setup until the connection is made
        while not self.listener:
            yield sleep(0.1)
        data = yield self.listener.read_bytes(1024, partial=True)

        auth_response = AuthResponsePacket()
        yield self.listener.write(bytes(auth_response))
        return data


class AuthenticateFailureTests(ListenerConnectionMixin, AsyncTestCase):

    def setUp(self):
        super(AuthenticateFailureTests, self).setUp()
        self.password = 'mypassword'

    @gen_test
    def test_exception_raised(self):
        """raise exception if server replies with different id"""
        yield self.make_listener_and_connect()

        with self.assertRaises(AuthenticationError):
            _, received_data = yield [
                authenticate(self.password, self.conn),
                self._listen_for_auth_request()
            ]

    @coroutine
    def _listen_for_auth_request(self):
        data = yield self.listener.read_bytes(1024, partial=True)

        auth_response = AuthResponsePacket()
        yield self.listener.write(bytes(auth_response))
        return data
