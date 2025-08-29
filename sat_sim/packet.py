# sat_sim/packet.py
"""
Packet framing, pack/unpack helpers, CRC-16/X25 implementation and
a simple delta+zlib compression helper.
"""

import struct
import zlib
from typing import Tuple

PREAMBLE = b'\xAA\x55'
VERSION = 0x01
MSGTYPE_TM = 0x01  # telemetry
MSGTYPE_CMD = 0x02  # uplink command

# ---------------------------------------------------
def pack_command(cmd_id: int, param: int = 0, seq: int = 0) -> bytes:
    """
    Small command frame (no big payload).
    Fields:
      PREAMBLE (2B)
      VERSION  (1B)
      MSGTYPE  (1B) = MSGTYPE_CMD
      SEQ      (2B) - optional sequence for traceability
      CMD_ID   (1B)
      PARAM    (4B) - signed int param
      CRC16    (2B)
    """
    import struct
    frame = bytearray()
    frame.extend(PREAMBLE)
    frame.extend(struct.pack('<B', VERSION))
    frame.extend(struct.pack('<B', MSGTYPE_CMD))
    frame.extend(struct.pack('<H', seq & 0xFFFF))
    frame.extend(struct.pack('<B', cmd_id & 0xFF))
    frame.extend(struct.pack('<i', int(param) & 0xFFFFFFFF))
    # CRC over bytes after preamble
    crc = crc16_x25(bytes(frame[2:]))
    frame.extend(struct.pack('<H', crc & 0xFFFF))
    return bytes(frame)


# ---------------- CRC-16/X25 (LSB-first, reflected poly 0x1021 -> use 0x8408)
def crc16_x25(data: bytes) -> int:
    """
    Compute CRC-16/X25 (poly 0x1021, reflected, init 0xFFFF, XOROUT 0xFFFF)
    Returns integer 0..0xFFFF
    """
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return crc ^ 0xFFFF

# ---------------- Frame packing/unpacking
def pack_telemetry(
    seq: int,
    timestamp_ms: int,
    mode: int,
    batt_mv: int,
    temp_centideg: int,
    press_pa: int,
    alt_cm: int,
    gyro_xyz: Tuple[int, int, int],
    acc_xyz: Tuple[int, int, int],
    light: int
) -> bytes:
    """
    Build a telemetry frame (binary).
    Fields (little-endian):
      PREAMBLE (2B)
      VERSION (1B)
      MSGTYPE (1B)
      SEQ (2B)
      TIMESTAMP_MS (4B)
      MODE (1B)
      BATT_MV (2B)
      TEMP_CENTI (2B signed)
      PRESS_PA (4B)
      ALT_CM (4B)
      GYRO_X,Y,Z (3 * int16)
      ACC_X,Y,Z  (3 * int16)
      LIGHT (2B)
      COMP_LEN (1B)  (0 for now)
      CRC16 (2B)
    """
    frame = bytearray()
    frame.extend(PREAMBLE)
    frame.extend(struct.pack('<B', VERSION))
    frame.extend(struct.pack('<B', MSGTYPE_TM))
    frame.extend(struct.pack('<H', seq & 0xFFFF))
    frame.extend(struct.pack('<I', timestamp_ms & 0xFFFFFFFF))
    frame.extend(struct.pack('<B', mode & 0xFF))
    frame.extend(struct.pack('<H', batt_mv & 0xFFFF))
    # temp (signed centi-degrees)
    frame.extend(struct.pack('<h', int(temp_centideg)))
    frame.extend(struct.pack('<I', int(press_pa) & 0xFFFFFFFF))
    frame.extend(struct.pack('<I', int(alt_cm) & 0xFFFFFFFF))
    frame.extend(struct.pack('<hhh', *gyro_xyz))
    frame.extend(struct.pack('<hhh', *acc_xyz))
    frame.extend(struct.pack('<H', int(light) & 0xFFFF))
    frame.extend(struct.pack('<B', 0))  # comp_len = 0 (no extra payload yet)

    # CRC over bytes AFTER preamble (i.e., from VERSION ... COMP_LEN)
    crc = crc16_x25(bytes(frame[2:]))
    frame.extend(struct.pack('<H', crc & 0xFFFF))
    return bytes(frame)


def unpack_frame(frame: bytes) -> dict:
    """
    Parse a frame and verify CRC. Returns dict of fields.
    Raises ValueError if preamble/CRC fail or frame too short.
    """
    min_len = 2 + 1 + 1 + 2 + 4 + 1 + 2 + 2 + 4 + 4 + 6 + 6 + 2 + 1 + 2
    if len(frame) < min_len:
        raise ValueError("Frame too short")

    if frame[0:2] != PREAMBLE:
        raise ValueError("Bad preamble")

    # CRC is last 2 bytes
    expected_crc = struct.unpack_from('<H', frame, len(frame) - 2)[0]
    computed_crc = crc16_x25(frame[2:-2])
    if expected_crc != computed_crc:
        raise ValueError(f"CRC mismatch: expected {hex(expected_crc)} vs computed {hex(computed_crc)}")

    idx = 2
    version = frame[idx]; idx += 1
    msgtype = frame[idx]; idx += 1
    seq = struct.unpack_from('<H', frame, idx)[0]; idx += 2
    timestamp_ms = struct.unpack_from('<I', frame, idx)[0]; idx += 4
    mode = frame[idx]; idx += 1
    batt_mv = struct.unpack_from('<H', frame, idx)[0]; idx += 2
    temp_centideg = struct.unpack_from('<h', frame, idx)[0]; idx += 2
    press_pa = struct.unpack_from('<I', frame, idx)[0]; idx += 4
    alt_cm = struct.unpack_from('<I', frame, idx)[0]; idx += 4
    gyro_x, gyro_y, gyro_z = struct.unpack_from('<hhh', frame, idx); idx += 6
    acc_x, acc_y, acc_z = struct.unpack_from('<hhh', frame, idx); idx += 6
    light = struct.unpack_from('<H', frame, idx)[0]; idx += 2
    comp_len = frame[idx]; idx += 1

    # CRC taken from frame tail already validated

    return {
        "version": version,
        "msgtype": msgtype,
        "seq": seq,
        "timestamp_ms": timestamp_ms,
        "mode": mode,
        "batt_mv": batt_mv,
        "temp_centideg": temp_centideg,
        "press_pa": press_pa,
        "alt_cm": alt_cm,
        "gyro": (gyro_x, gyro_y, gyro_z),
        "acc": (acc_x, acc_y, acc_z),
        "light": light,
        "comp_len": comp_len,
        "raw_frame_len": len(frame)
    }

# ---------------- compression helper (delta + zlib)
def delta_pack_and_compress(prev_vals: list, cur_vals: list) -> Tuple[bytes, bool]:
    """
    Build delta array (int16 each) from prev to cur, pack as little-endian int16s,
    then try zlib compression. Return (payload_bytes, compressed_flag).
    """
    if len(prev_vals) != len(cur_vals):
        raise ValueError("prev/cur length mismatch")
    deltas = [int(c - p) for p, c in zip(prev_vals, cur_vals)]
    packed = struct.pack('<' + 'h' * len(deltas), *deltas)
    comp = zlib.compress(packed)
    if len(comp) < len(packed):
        return comp, True
    else:
        return packed, False

