from unittest import TestCase

from srcrcon.command import Command
from srcrcon.utils import fancy
from srcrcon.exceptions import InvalidCommandError


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
