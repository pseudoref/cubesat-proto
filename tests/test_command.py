# tests/test_command.py
import unittest
from sat_sim.packet import pack_command, unpack_command, MSGTYPE_CMD

class CmdTest(unittest.TestCase):
    def test_cmd_roundtrip(self):
        frame = pack_command(cmd_id=1, param=2, seq=42)
        parsed = unpack_command(frame)
        self.assertEqual(parsed["msgtype"], MSGTYPE_CMD)
        self.assertEqual(parsed["seq"], 42)
        self.assertEqual(parsed["cmd_id"], 1)
        self.assertEqual(parsed["param"], 2)

if __name__ == '__main__':
    unittest.main()

