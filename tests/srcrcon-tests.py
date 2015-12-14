from unittest import TestCase
import unittest.mock as mock
from argparse import ArgumentParser, Namespace
from asyncio import coroutine

from tornado.concurrent import Future
from tornado.testing import AsyncTestCase, gen_test

from testing import FuncToolsPartialMatcher
from srcrcon.command import Command
from srcrcon import SrcRCON


class TestCommand1(Command):
    name = 'listplayers'
    help = 'list all players'
    command_fmt = 'ListPlayers'

    def validate(self, response):
        return True


class TestCommand2(Command):
    name = 'saytoplayer'
    help = 'send a message to a player'
    args = [
        dict(name='player_name', help='name of player'),
        dict(name='message', help='message to send'),
    ]
    command_fmt = 'SayToPlayer {player_name} {message}'

    def validate(self, response):
        return True


class SrcRCONTests(TestCase):

    @mock.patch('srcrcon.srcrcon.new_parser', spec=ArgumentParser)
    def setUp(self, _new_parser):
        self._new_parser = _new_parser
        self._parser = mock.MagicMock()
        self._new_parser.return_value = self._parser

        self._subparser = mock.MagicMock()
        self._subparsers = mock.MagicMock()
        self._parser.add_subparsers.return_value = self._subparsers
        self._subparsers.add_parser.return_value = self._subparser

        self.app = SrcRCON()
        self.app.register_commands(
            *[TestCommand1, TestCommand2],
            title='mytitle',
            description='mydescription',
            help='myhelp'
        )

    def test_subparser_added(self):
        """a sub-parser should be added for each command"""
        self._parser.add_subparsers.assert_called_once_with(
            title='mytitle',
            description='mydescription',
            help='myhelp'
        )

    def test_first_command_added(self):
        self._subparsers.add_parser.assert_any_call(
            'listplayers',
            help='list all players'
        )

    def test_second_command_added(self):
        self._subparsers.add_parser.assert_any_call(
            'saytoplayer',
            help='send a message to a player'
        )

    def test_second_command_arguments_added(self):
        calls = [
            mock.call('player_name', help='name of player'),
            mock.call('message', help='message to send'),
        ]
        self._subparser.add_argument.assert_has_calls(calls)

    def test_func_set(self):
        calls = [
            mock.call(func=FuncToolsPartialMatcher(self.app._invoke_command, TestCommand1)),
            mock.call(func=FuncToolsPartialMatcher(self.app._invoke_command, TestCommand2)),
        ]
        self._subparser.set_defaults.assert_has_calls(calls)


class MockAuthenticate(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class MockExecute(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class SrcRCONSingleParseTests(AsyncTestCase):

    def setUp(self):
        super().setUp()

        self._conn = mock.MagicMock()

        self.app = SrcRCON()
        self.app.register_commands(
            *[TestCommand1, TestCommand2],
            title='mytitle',
            description='mydescription',
            help='myhelp'
        )

        self.args = [
            '--host', 'localhost',
            '--port', '1234',
            '--password', 'mypass',
            'saytoplayer', 'Bobby', 'do the thing!',
        ]
        self.parsed_args = Namespace(
            host='localhost',
            port=1234,
            password='mypass',
            player_name='Bobby',
            message='do the thing!',
        )
        self.coro = self.app.start(*self.args)

    @mock.patch('srcrcon.srcrcon.execute', new_callable=MockExecute)
    @mock.patch('srcrcon.srcrcon.authenticate', new_callable=MockAuthenticate)
    @gen_test
    def test_authenticate(self, _authenticate, _execute):
        yield self.coro
        _authenticate.assert_called_once_with(
            'mypass', host='localhost', port=1234
        )

    @mock.patch('srcrcon.srcrcon.execute', new_callable=MockExecute)
    @mock.patch('srcrcon.srcrcon.authenticate', new_callable=MockAuthenticate)
    @gen_test
    def test_execute(self, _authenticate, _execute):
        _authenticate.return_value = self._conn
        yield self.coro
        _execute.assert_called_once_with(
            TestCommand2(self.parsed_args),
            self._conn
        )
