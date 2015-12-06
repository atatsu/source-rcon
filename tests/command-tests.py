import random
from unittest import skip, TestCase
import unittest.mock as mock

from tornado.ioloop import TimeoutError
from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test
from colorama import Fore, Back, Style

from testing import ListenerConnectionMixin

from srcrcon.protocol import ExecCommandPacket, ResponseValuePacket
from srcrcon.command import fancy, execute, Command
from srcrcon.exceptions import InvalidCommandError, CommandError


class FancyTests(TestCase):

    @mock.patch('colorama.init')
    def setUp(self, _init):
        fancy._initialized = False
        self._init = _init
        self.colorized = fancy('color at me, bro', 'yellow', 'red', 'bright')
        self.defaults = fancy('nothing special', 'badfg', 'badbg', 'badstyle')

    def test_colors_mapped(self):
        expected = '{}{}{}color at me, bro{}'.format(
            Fore.YELLOW, Back.RED, Style.BRIGHT, Style.RESET_ALL
        )
        self.assertEquals(expected, self.colorized)

    def test_colors_initialized_once(self):
        self._init.assert_called_once_with()

    def test_sane_fallbacks(self):
        expected = 'nothing special{}'.format(Style.RESET_ALL)
        self.assertEquals(expected, self.defaults)


class CommandTests(TestCase):

    def setUp(self):
        self.cmd = Command('do stuff')

    def test_nice_default_success(self):
        expected = fancy('{!r} succeeded.'.format('do stuff'), fg='green')
        self.assertEquals(expected, self.cmd.success)

    def test_nice_default_failure(self):
        expected = fancy('{!r} failed!'.format('do stuff'), fg='red')
        self.assertEquals(expected, self.cmd.failure)

    def test_error_no_command(self):
        with self.assertRaises(InvalidCommandError) as cm:
            cmd = Command()
        self.assertEquals('Expected a command string', str(cm.exception))


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
        with self.assertRaises(CommandError):
            yield self._do_everything()

    @mock.patch('builtins.print')
    @gen_test
    def test_prints_failure_msg(self, _print):
        with self.assertRaises(CommandError):
            yield self._do_everything()
        _print.assert_called_once_with(self.cmd.failure)
