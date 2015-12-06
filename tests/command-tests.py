import random
from unittest import skip
import unittest.mock as mock

from tornado.ioloop import TimeoutError
from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test

from testing import ListenerConnectionMixin

from srcrcon.protocol import ExecCommandPacket, ResponseValuePacket
from srcrcon.command import execute, Command


class ExecTestsMixin:

    request_id = 5
    response_id = 5

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

    @gen_test
    def test_notifies_success(self):
        exec_result, _ = yield self._do_everything()
        self.assertTrue(exec_result, "`execute` didn't return `True`")

    @mock.patch('builtins.print')
    @gen_test
    def test_should_print_success_msg(self, _print):
        yield self._do_everything()
        _print.assert_called_once_with(self.cmd.success)


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
        exec_result, _ = yield self._do_everything()
        self.assertFalse(exec_result, "`execute` didn't return `False`")

    @mock.patch('builtins.print')
    @gen_test
    def test_prints_failure_msg(self, _print):
        yield self._do_everything()
        _print.assert_called_once_with(self.cmd.failure)
