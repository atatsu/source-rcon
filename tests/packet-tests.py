import unittest
import unittest.mock as mock

import srcrcon


class PacketTests(unittest.TestCase):

    @mock.patch('random.randint')
    def setUp(self, _randint):
        _randint.return_value = 5
        self.packet = srcrcon.packet.Packet()

    def test_should_have_id(self):
        self.assertEquals(5, self.packet.id)
