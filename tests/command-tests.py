from unittest import TestCase, skip
from argparse import Namespace

from srcrcon.command import Command, Argument
from srcrcon.utils import fancy


class TestArgument(Argument):
    pass


class TestCommand(Command):

    command_fmt = 'SayToPlayer {player_name!r} {message}'

    def validate(self, reponse):
        pass


class ArgumentTests(TestCase):

    def test_get_name(self):
        self.assertEquals('test_argument', TestArgument.get_name())

    def test_fmt(self):
        self.assertEquals('{test_argument}', TestArgument.fmt())


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

    @skip('not sure if this is necessary')
    def test_ne(self):
        self.assertNotEquals(TestCommand(Namespace()), TestCommand(Namespace(one='two')))
