import unittest
import unittest.mock as mock
import argparse
import functools

from testing import FuncToolsPartialMatcher
from srcrcon.command import Command
from srcrcon import SrcRCON


class CliArgs:
    def __init__(self):
        pass

    def add(self, arg, help=None):
        return self


class TestCommand1(Command):
    name = 'listplayers'
    help = 'list all players'
    command_text = 'ListPlayers'


class TestCommand2(Command):
    name = 'saytoplayer'
    help = 'send a message to a player'
    args = [
        dict(name='player_name', help='name of player'),
        dict(name='message', help='message to send'),
    ]
    command_text = 'SayToPlayer {player_name} {message}'


class SrcRCONTests(unittest.TestCase):

    @mock.patch('srcrcon.srcrcon.parser', spec=argparse.ArgumentParser)
    def setUp(self, _argparser):
        self._argparser = _argparser
        self._subparser = mock.MagicMock()
        self._subparsers = mock.MagicMock()
        self._argparser.add_subparsers.return_value = self._subparsers
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
        self._argparser.add_subparsers.assert_called_once_with(
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
