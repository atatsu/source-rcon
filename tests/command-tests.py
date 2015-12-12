import random
from unittest import skip, TestCase
import unittest.mock as mock

from tornado.ioloop import TimeoutError
from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test

from testing import ListenerConnectionMixin

from srcrcon.protocol import ExecCommandPacket, ResponseValuePacket
from srcrcon.command import execute, Command
from srcrcon.utils import fancy
from srcrcon.exceptions import InvalidCommandError, CommandError


class CommandTests(TestCase):

    def setUp(self):
        self.cmd = Command('do stuff')

    def test_nice_default_success(self):
        expected = fancy('{!r} succeeded.'.format('do stuff'), fg='green')
        self.assertEquals(expected, self.cmd.success)

    def test_nice_default_failure(self):
        expected = fancy('{!r} failed!'.format('do stuff'), fg='red')
        self.assertEquals(expected, self.cmd.failure)

    def test_nice_default_response(self):
        expected = fancy('{response}', fg='yellow')
        self.assertEquals(expected, self.cmd.response)

    def test_error_no_command(self):
        with self.assertRaises(InvalidCommandError) as cm:
            cmd = Command()
        self.assertEquals('Expected a command string', str(cm.exception))


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
