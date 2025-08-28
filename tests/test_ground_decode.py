# tests/test_ground_decode.py
import unittest
from sat_sim.packet import pack_telemetry
from ground.decode import decode_datagram

class TestGroundDecode(unittest.TestCase):
    def test_decode_roundtrip(self):
        frame = pack_telemetry(
            seq=42, timestamp_ms=123456, mode=1,
            batt_mv=3950, temp_centideg=2612,
            press_pa=101111, alt_cm=999,
            gyro_xyz=(5, -2, 0), acc_xyz=(100, 0, 950), light=700
        )
        row = decode_datagram(frame)
        self.assertEqual(row["seq"], 42)
        self.assertEqual(row["mode"], "SAFE")
        self.assertAlmostEqual(row["temp_c"], 26.12, places=2)

if __name__ == "__main__":
    unittest.main()

