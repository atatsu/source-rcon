import unittest
import unittest.mock as mock
import struct

import srcrcon


class PacketTests(unittest.TestCase):

    @mock.patch('random.randint')
    def setUp(self, _randint):
        _randint.return_value = 5
        self.packet = srcrcon.packet.Packet()
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
        p = srcrcon.packet.Packet()
        with self.assertRaises(AttributeError) as cm:
            bytes(p)
        self.assertEquals(
            'Missing `type`',
            str(cm.exception)
        )

class ServerDataAuthResponseTests(unittest.TestCase):

    @mock.patch('random.randint')
    def setUp(self, _randint):
        p = srcrcon.packet.ServerDataAuth(1234)
        _randint.return_value = 5

        self.body = bytes(chr(0x00), 'ascii')
        payload = struct.pack(
            srcrcon.packet.Packet._pack_format.format(body_len=len(self.body)),
            struct.calcsize(
                srcrcon.packet.Packet._pack_format.format(body_len=len(self.body))
            ) - 4,
            25, # id
            srcrcon.packet.ServerDataAuthResponse.type,
            self.body
        )
        self.packet = srcrcon.packet.Packet(raw=payload[4:])

    def test_correct_type(self):
        self.assertTrue(
            isinstance(self.packet, srcrcon.packet.ServerDataAuthResponse),
            '{} != ServerDataAuthResponse'.format(type(self.packet))
        )

    def test_id_set(self):
        self.assertEquals(25, self.packet.id)

class ServerDataResponseValueCreationTests(unittest.TestCase):

    @mock.patch('random.randint')
    def setUp(self, _randint):
        _randint.return_value = 5

        self.body = b'i did stuff'
        payload = struct.pack(
            srcrcon.packet.Packet._pack_format.format(body_len=len(self.body)),
            struct.calcsize(
                srcrcon.packet.Packet._pack_format.format(body_len=len(self.body))
            ) - 4,
            25, # id
            srcrcon.packet.ServerDataResponseValue.type,
            self.body
        )
        # strip off `size`
        self.packet = srcrcon.packet.Packet(raw=payload[4:])

    def test_correct_type(self):
        self.assertTrue(
            isinstance(self.packet, srcrcon.packet.ServerDataResponseValue),
            '{} != ServerDataResponseValue'.format(type(self.packet))
        )

    def test_id_set(self):
        self.assertEquals(25, self.packet.id)

    def test_body_set(self):
        self.assertEquals(self.body, self.packet.body)
