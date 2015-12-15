from unittest import TestCase
import unittest.mock as mock
from argparse import ArgumentParser, Namespace
from asyncio import coroutine
from collections import OrderedDict

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


class SrcRCONParserSetupTests(TestCase):

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
        self.coro = self.app.init(*self.args)

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


class MockFunc(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class SrcRCONConfigTests(AsyncTestCase):

    @mock.patch('srcrcon.srcrcon.new_parser')
    def setUp(self, _new_parser):
        super().setUp()

        config_patcher = mock.patch('srcrcon.srcrcon.ConfigParser', autospec=True)
        self._configparser = config_patcher.start()
        self._configparser.return_value = self._configparser
        self.configFile = dict(mysection=OrderedDict(
            [('host', 'localhost'), ('port', '5555'), ('password', 'mypass')]
        ))
        self._configparser.__getitem__.side_effect = lambda x: self.configFile[x]

        self._argparser = mock.Mock(spec=ArgumentParser)
        _new_parser.return_value = self._argparser

        self.app = SrcRCON()
        self.app.register_commands(*[TestCommand1, TestCommand2])
        self.args = [
            '-c', '~/.source-rcon.cfg',
            'listplayers',
        ]
        self._func = MockFunc()
        self.parsed_args = Namespace(
            config='~/.source-rcon.cfg=mysection',
            loglevel=None,
            func=self._func
        )

        self._argparser.parse_args.return_value = self.parsed_args

        self.coro = self.app.init(*self.args)

        self.addCleanup(mock.patch.stopall)

    @gen_test
    def test_file_read(self):
        yield self.coro
        self._configparser.read.assert_called_once_with('~/.source-rcon.cfg')

    @gen_test
    def test_args_updated(self):
        yield self.coro
        print(self._argparser.parse_args.call_args_list)
        self._argparser.parse_args.assert_any_call(
            ['--host', 'localhost', '--port', '5555', '--password', 'mypass'],
            namespace=self.parsed_args
        )
