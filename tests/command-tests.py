from unittest import skip
import unittest.mock as mock

from tornado.ioloop import TimeoutError
from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test

from testing import ListenerConnectionMixin

from srcrcon.protocol import ExecCommandPacket, ResponseValuePacket
from srcrcon.command import execute, Command


class ExecSuccessTests(ListenerConnectionMixin, AsyncTestCase):

    def setUp(self):
        super(ExecSuccessTests, self).setUp()
        self.cmd = Command('do stuff', 'you did it!')

    @skip('not implemented')
    def test_active_conn_only(self):
        """should only allow active connections"""

    @skip('not implemented')
    def test_auth_conn_only(self):
        """should only allow authenticated connections"""

    @mock.patch('random.randint')
    @gen_test
    def test_sends_command(self, _randint):
        _randint.return_value = 5
        expected = ExecCommandPacket(str(self.cmd))
        exec_result, listened_data = yield self._do_everything()
        self.assertEquals(bytes(expected), listened_data)

    @mock.patch('random.randint')
    @gen_test
    def test_notifies_success(self, _randint):
        _randint.return_value = 5
        exec_result, listened_data = yield self._do_everything()
        self.assertTrue(exec_result, "`execute` didn't return `True`")

    @mock.patch('builtins.print')
    @mock.patch('random.randint')
    @gen_test
    def test_should_print_results(self, _randint, _print):
        _randint.return_value = 5
        yield self._do_everything()
        _print.assert_called_once_with(self.cmd.success)

    @coroutine
    def _do_everything(self):
        yield self.make_listener_and_connect()
        exec_action = execute(self.cmd, self.conn)
        listen_action = self._listen_for_requests()
        exec_result, listened_data = yield [exec_action, listen_action]

        return (exec_result, listened_data)

    @coroutine
    def _listen_for_requests(self):
        data = yield self.listener.read_bytes(1024, partial=True)

        resp = ResponseValuePacket()
        yield self.listener.write(bytes(resp))

        return data
