import unittest
import unittest.mock as mock
import struct

import srcrcon


class PacketTests(unittest.TestCase):

    @mock.patch('random.randint')
    def setUp(self, _randint):
        _randint.return_value = 5
        self.packet = srcrcon.protocol.Packet()
        self.packet.type = 0
        self.packet.body = 'herro'

    def test_should_have_id(self):
        self.assertEquals(5, self.packet.id)

    def test_size(self):
        # 4 - id, 4 - type, 5 - body, 2 - NULs
        self.assertEquals(15, self.packet.size)

    def test_bytes(self):
        expected = struct.pack(
            '<iii5sxx',
            self.packet.size,
            self.packet.id,
            self.packet.type,
            bytes(self.packet.body, 'ascii')
        )
        actual = bytes(self.packet)
        self.assertEquals(expected, actual)


class PacketErrorTests(unittest.TestCase):

    def test_no_type(self):
        p = srcrcon.protocol.Packet()
        with self.assertRaises(AttributeError) as cm:
            bytes(p)
        self.assertEquals(
            'Missing `type`',
            str(cm.exception)
        )

class AuthResponseTests(unittest.TestCase):

    @mock.patch('random.randint')
    def setUp(self, _randint):
        p = srcrcon.protocol.Auth(1234)
        _randint.return_value = 5

        self.body = bytes(chr(0x00), 'ascii')
        payload = struct.pack(
            srcrcon.protocol.Packet._pack_format.format(body_len=len(self.body)),
            struct.calcsize(
                srcrcon.protocol.Packet._pack_format.format(body_len=len(self.body))
            ) - 4,
            25, # id
            srcrcon.protocol.AuthResponse.type,
            self.body
        )
        self.packet = srcrcon.protocol.Packet(raw=payload[4:])

    def test_correct_type(self):
        self.assertTrue(
            isinstance(self.packet, srcrcon.protocol.AuthResponse),
            '{} != AuthResponse'.format(type(self.packet))
        )

    def test_id_set(self):
        self.assertEquals(25, self.packet.id)

class ResponseValueCreationTests(unittest.TestCase):

    @mock.patch('random.randint')
    def setUp(self, _randint):
        _randint.return_value = 5

        self.body = b'i did stuff'
        payload = struct.pack(
            srcrcon.protocol.Packet._pack_format.format(body_len=len(self.body)),
            struct.calcsize(
                srcrcon.protocol.Packet._pack_format.format(body_len=len(self.body))
            ) - 4,
            25, # id
            srcrcon.protocol.ResponseValue.type,
            self.body
        )
        # strip off `size`
        self.packet = srcrcon.protocol.Packet(raw=payload[4:])

    def test_correct_type(self):
        self.assertTrue(
            isinstance(self.packet, srcrcon.protocol.ResponseValue),
            '{} != ResponseValue'.format(type(self.packet))
        )

    def test_id_set(self):
        self.assertEquals(25, self.packet.id)

    def test_body_set(self):
        self.assertEquals(self.body, self.packet.body)
