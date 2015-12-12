import unittest.mock as mock
from unittest import skip

from tornado.gen import coroutine, sleep
from tornado.testing import AsyncTestCase, gen_test

from testing import ListenerConnectionMixin

from srcrcon.command import Command
from srcrcon.protocol import (AuthPacket,
                              AuthResponsePacket,
                              ExecCommandPacket,
                              ResponseValuePacket)
from srcrcon.connection import authenticate, Connection, execute
from srcrcon.exceptions import AuthenticationError, ConnectionError, CommandError


class ConnectionConnectTests(ListenerConnectionMixin, AsyncTestCase):
    """Connection.connect()"""

    connected = False

    @gen_test
    def test_should_connect(self):
        yield self.conn.connect()
        self.assertTrue(self.connected, "Didn't connect!")

    def _on_connected(self, connection, address):
        self.connected = True

    @gen_test
    def test_connect_error_raises(self):
        conn = Connection('127.0.0.1', self.port + 1)
        with self.assertRaises(ConnectionError) as cm:
            yield conn.connect()
        self.assertEquals("('127.0.0.1', {:d})".format(self.port + 1), str(cm.exception))


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


class ExecTestsMixin:

    request_id = 5
    response_id = 5
    response_body = 'gg'

    @coroutine
    def _do_everything(self):
        with mock.patch('random.randint', return_value=self.request_id):
            yield self.make_listener_and_connect()
            exec_action = execute(self.cmd, self.conn)
            listen_action = self._listen_for_requests()
            exec_result, listened_data = yield [exec_action, listen_action]

            return (exec_result, listened_data)

    @coroutine
    def _listen_for_requests(self):
        data = yield self.listener.read_bytes(1024, partial=True)

        resp = ResponseValuePacket()
        resp.id = self.response_id
        resp.body = self.response_body
        yield self.listener.write(bytes(resp))

        return data


class ExecSuccessTests(ListenerConnectionMixin, AsyncTestCase, ExecTestsMixin):

    def setUp(self):
        super(ExecSuccessTests, self).setUp()
        self.cmd = Command('do stuff', 'you did it!')

    @gen_test
    def test_sends_command(self):
        expected = ExecCommandPacket(str(self.cmd))
        expected.id = self.request_id
        _, listened_data = yield self._do_everything()
        self.assertEquals(bytes(expected), listened_data)

    @mock.patch('builtins.print')
    @gen_test
    def test_should_print_success_msg(self, _print):
        yield self._do_everything()
        _print.assert_any_call(self.cmd.success)

    @mock.patch('builtins.print')
    @gen_test
    def test_should_print_server_response(self, _print):
        yield self._do_everything()
        _print.assert_any_call(self.cmd.response.format(response=(self.response_body)))


class ExecFailureTests(ListenerConnectionMixin, AsyncTestCase, ExecTestsMixin):

    response_id = 6

    def setUp(self):
        super(ExecFailureTests, self).setUp()
        self.cmd = Command('do stuff', failure='ohnoes!')

    @skip('not implemented')
    def test_active_conn_only(self):
        """should only allow active connections"""

    @skip('not implemented')
    def test_auth_conn_only(self):
        """should only allow authenticated connections"""

    @gen_test
    def test_notifies_failure(self):
        with self.assertRaises(CommandError):
            yield self._do_everything()

    @mock.patch('builtins.print')
    @gen_test
    def test_prints_failure_msg(self, _print):
        with self.assertRaises(CommandError):
            yield self._do_everything()
        _print.assert_called_once_with(self.cmd.failure)
