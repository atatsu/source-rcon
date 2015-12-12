from unittest import TestCase
import unittest.mock as mock

from colorama import Fore, Back, Style

from srcrcon.utils import fancy


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
