# tests/test_packet.py
import unittest
from sat_sim.packet import pack_telemetry, unpack_frame

class PacketTest(unittest.TestCase):
    def test_roundtrip(self):
        seq = 123
        ts = 987654321
        frame = pack_telemetry(
            seq=seq, timestamp_ms=ts, mode=0,
            batt_mv=4100, temp_centideg=2534,
            press_pa=101325, alt_cm=1000,
            gyro_xyz=(10, -10, 5), acc_xyz=(100, -50, 980), light=512
        )
        parsed = unpack_frame(frame)
        self.assertEqual(parsed['seq'], seq)
        self.assertEqual(parsed['timestamp_ms'], ts)
        self.assertEqual(parsed['batt_mv'], 4100)
        self.assertEqual(parsed['temp_centideg'], 2534)

if __name__ == '__main__':
    unittest.main()

