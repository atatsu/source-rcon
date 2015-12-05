import unittest.mock as mock

from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test

from testing import ListenerConnectionMixin

from srcrcon.protocol import AuthPacket, AuthResponsePacket
from srcrcon.auth import Auth
from srcrcon.exceptions import AuthenticationFailure


class AuthSuccessTests(ListenerConnectionMixin, AsyncTestCase):

    def setUp(self):
        super(AuthSuccessTests, self).setUp()
        self.password = 'mypassword'

    @mock.patch('random.randint')
    @gen_test
    def test_authentication(self, _randint):
        """return connection and be `authenticated` if server replies with same id"""
        _randint.return_value = 5

        yield self.make_listener_and_connect()
        authenticator = Auth(self.password, self.conn)

        _, received_data = yield [
            authenticator.authenticate(),
            self._listen_for_auth_request()
        ]

        auth_check = AuthPacket(self.password)
        self.assertEquals(bytes(auth_check), received_data, 'client sent non-auth request')
        self.assertTrue(authenticator.authenticated, 'not authenticated')

    @coroutine
    def _listen_for_auth_request(self):
        data = yield self.listener.read_bytes(1024, partial=True)

        auth_response = AuthResponsePacket()
        yield self.listener.write(bytes(auth_response))
        return data


class AuthFailureTests(ListenerConnectionMixin, AsyncTestCase):

    def setUp(self):
        super(AuthFailureTests, self).setUp()
        self.password = 'mypassword'

    @gen_test
    def test_authentication(self):
        """raise exception if server replies with different id"""
        yield self.make_listener_and_connect()
        authenticator = Auth(self.password, self.conn)

        with self.assertRaises(AuthenticationFailure):
            _, received_data = yield [
                authenticator.authenticate(),
                self._listen_for_auth_request()
            ]

    @coroutine
    def _listen_for_auth_request(self):
        data = yield self.listener.read_bytes(1024, partial=True)

        auth_response = AuthResponsePacket()
        yield self.listener.write(bytes(auth_response))
        return data
