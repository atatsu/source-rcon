import unittest
import unittest.mock as mock
import struct

from srcrcon.protocol import Packet, AuthPacket, AuthResponsePacket, ResponseValuePacket


class PacketTests(unittest.TestCase):

    @mock.patch('random.randint')
    def setUp(self, _randint):
        _randint.return_value = 5
        self.packet = Packet()
        self.packet.type = 0
        self.packet.body = 'herro'

    def test_should_have_id(self):
        self.assertEquals(5, self.packet.id)

    def test_size(self):
        # 4 - id, 4 - type, 5 - body, 2 - NULs
        self.assertEquals(15, len(self.packet))

    def test_bytes(self):
        expected = struct.pack(
            '<iii5sxx',
            len(self.packet),
            self.packet.id,
            self.packet.type,
            bytes(self.packet.body, 'ascii')
        )
        actual = bytes(self.packet)
        self.assertEquals(expected, actual)

    def test_readable_representation(self):
        expected = "Packet(size=15, id=5, type=0, body='herro')"
        actual = str(self.packet)
        self.assertEquals(expected, actual)

    def test_equality(self):
        packet = Packet()
        packet.id = 5
        packet.type = 0
        packet.body = 'herro'

        self.assertEquals(packet, self.packet)


class PacketErrorTests(unittest.TestCase):

    def test_no_type(self):
        p = Packet()
        with self.assertRaises(AttributeError) as cm:
            bytes(p)
        self.assertEquals(
            'Missing `type`',
            str(cm.exception)
        )


class AuthPacketTests(unittest.TestCase):
    """Assert that an `AuthPacket` packet packs correctly."""

    @mock.patch('random.randint')
    def setUp(self, _randint):
        _randint.return_value = 5
        self.body = 'mypassword'
        self.actual = bytes(AuthPacket(self.body))

    def test_packs_correctly(self):
        size = struct.calcsize('<ii{}sxx'.format(len(self.body)))
        expected = struct.pack(
            '<iii{}sxx'.format(len(self.body)),
            size,
            5,
            AuthPacket.type,
            bytes(self.body, 'ascii')
        )
        self.assertEquals(expected, self.actual)

class AuthResponsePacketTests(unittest.TestCase):
    """Assert that an `AuthResponsePacket` packet unpacks correctly."""

    @mock.patch('random.randint')
    def setUp(self, _randint):
        p = AuthPacket(1234)
        _randint.return_value = 5

        self.body = bytes(chr(0x00), 'ascii')
        payload = struct.pack(
            Packet._pack_format.format(body_len=len(self.body)),
            struct.calcsize(
                Packet._pack_format.format(body_len=len(self.body))
            ) - 4,
            25, # id
            AuthResponsePacket.type,
            self.body
        )
        self.packet = Packet(raw=payload[4:])

    def test_correct_type(self):
        self.assertTrue(
            isinstance(self.packet, AuthResponsePacket),
            '{} != AuthResponsePacket'.format(type(self.packet))
        )

    def test_id_set(self):
        self.assertEquals(25, self.packet.id)

class ResponseValuePacketTests(unittest.TestCase):
    """Assert that a `ResponseValuePacket` packet unpacks correctly."""

    @mock.patch('random.randint')
    def setUp(self, _randint):
        _randint.return_value = 5

        self.body = 'i did stuff'
        payload = struct.pack(
            Packet._pack_format.format(body_len=len(self.body)),
            struct.calcsize(
                Packet._pack_format.format(body_len=len(self.body))
            ) - 4,
            25, # id
            ResponseValuePacket.type,
            bytes(self.body, 'ascii')
        )
        # strip off `size`
        self.packet = Packet(raw=payload[4:])

    def test_correct_type(self):
        self.assertTrue(
            isinstance(self.packet, ResponseValuePacket),
            '{} != ResponseValuePacket'.format(type(self.packet))
        )

    def test_id_set(self):
        self.assertEquals(25, self.packet.id)

    def test_body_set(self):
        self.assertEquals(self.body, self.packet.body)
