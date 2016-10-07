import unittest.mock as mock
from unittest import TestCase

from srcrcon.notify import ConsoleNotifier


class ConsoleNotifierTests(TestCase):

    def setUp(self):
        self.notifier = ConsoleNotifier()

    @mock.patch('builtins.print')
    def test_notify_prints(self, _print):
        self.notifier.notify('telling you stuff')
        _print.assert_called_once_with('telling you stuff')
