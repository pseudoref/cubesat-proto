import unittest
from sat_sim.packet import pack_command, unpack_frame

class CmdTest(unittest.TestCase):
    def test_cmd_roundtrip(self):
        frame = pack_command(cmd_id=1, param=2, seq=42)
        parsed = unpack_frame(frame)
        self.assertEqual(parsed['msgtype'], 0x02)
        # parse payload manually
        import struct
        cmd_id = frame[6]
        param = struct.unpack_from('<i', frame, 7)[0]
        self.assertEqual(cmd_id, 1)
        self.assertEqual(param, 2)

if __name__ == '__main__':
    unittest.main()

