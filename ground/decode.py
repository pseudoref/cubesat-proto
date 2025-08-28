# ground/decode.py
from typing import Dict
from sat_sim.packet import unpack_frame

MODE_MAP = {0: "OP", 1: "SAFE", 2: "IDLE"}

def decode_datagram(data: bytes) -> Dict:
    """
    Takes a single UDP datagram (one frame), validates CRC via unpack_frame,
    converts a few fields into human-friendly forms, and returns dict.
    Raises ValueError if frame is invalid.
    """
    try:
        f = unpack_frame(data)  # may raise ValueError (bad preamble/CRC/len)
    except Exception as e:
        # Explicitly re-raise as ValueError for ground loop consistency
        raise ValueError(f"Failed to unpack frame: {e}")

    return {
        "version": int(f["version"]),
        "msgtype": int(f["msgtype"]),
        "seq": int(f["seq"]),
        "timestamp_ms": int(f["timestamp_ms"]),
        "mode": MODE_MAP.get(f["mode"], str(f["mode"])),
        "batt_mv": int(f["batt_mv"]),
        "temp_c": round(f["temp_centideg"] / 100.0, 2),
        "press_pa": int(f["press_pa"]),
        "alt_cm": int(f["alt_cm"]),
        "gyro_x": int(f["gyro"][0]),
        "gyro_y": int(f["gyro"][1]),
        "gyro_z": int(f["gyro"][2]),
        "acc_x": int(f["acc"][0]),
        "acc_y": int(f["acc"][1]),
        "acc_z": int(f["acc"][2]),
        "light": int(f["light"]),
        "comp_len": int(f["comp_len"]),
        "raw_len": int(f["raw_frame_len"]),
    }

