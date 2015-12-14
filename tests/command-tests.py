from unittest import TestCase
from argparse import Namespace

from srcrcon.command import Command
from srcrcon.utils import fancy


class TestCommand(Command):

    command_fmt = 'SayToPlayer {player_name!r} {message}'

    def validate(self, reponse):
        pass


class CommandTests(TestCase):

    def setUp(self):
        self.parsed_args = Namespace(
            player_name='Eggsy',
            message='do stuff'
        )
        self.cmd = TestCommand(self.parsed_args)

    def test_str_to_command_text(self):
        expected = "SayToPlayer 'Eggsy' do stuff"
        actual = str(self.cmd)
        self.assertEquals(expected, actual)

    def test_repr(self):
        expected = '"SayToPlayer \'Eggsy\' do stuff"'
        actual = repr(self.cmd)
        self.assertEquals(expected, actual)

    def test_success(self):
        expected = fancy(
            '{!r} succeeded.'.format("SayToPlayer 'Eggsy' do stuff"),
            fg='green'
        )
        self.assertEquals(expected, self.cmd.success())

    def test_failure(self):
        expected = fancy(
            '{!r} failed!'.format("SayToPlayer 'Eggsy' do stuff"),
            fg='red'
        )
        self.assertEquals(expected, self.cmd.failure())

    def test_server_response(self):
        expected = fancy('I did stuff', fg='yellow')
        self.assertEquals(expected, self.cmd.response('I did stuff'))

    def test_eq(self):
        self.assertEquals(TestCommand(Namespace()), TestCommand(Namespace()))

    def test_ne(self):
        self.assertNotEquals(TestCommand(Namespace()), TestCommand(Namespace(one='two')))
