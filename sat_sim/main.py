# sat_sim/main.py
import random
import time
import json
import os
import threading
from .sensors import SensorSimulator
from .packet import pack_telemetry, pack_command, unpack_frame, MSGTYPE_CMD
from .link import UDPSender
from .fsm import CubeSatFSM
from .command_listener import CommandListener

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def main():
    cfg = load_config()
    sim = SensorSimulator(cfg)
    fsm = CubeSatFSM(temp_high_centi=4000, batt_low_mv=3300)
    sender = UDPSender(cfg.get('udp_host', '127.0.0.1'), cfg.get('udp_port', 5005))

    # uplink listener callback
    def on_command(datagram, addr):
        try:
            # reuse unpack_frame to examine header; unpack_frame may raise on CRC fail
            info = unpack_frame(datagram)
        except Exception as e:
            print("Received bad uplink frame:", e)
            return
        if info.get("msgtype") != MSGTYPE_CMD:
            print("Ignoring non-command uplink frame (msgtype=%s)" % info.get("msgtype"))
            return
        # parse cmd_id and param from payload portion (we packed cmd_id (1B) + param (4B) after seq)
        # compute where payload starts: preamble(2) + VERSION(1)+MSGTYPE(1)+SEQ(2) = 6 bytes after preamble => index 2+1+1+2 = 6
        # but unpack_frame consumes and returns values; easiest is to parse raw bytes:
        raw = datagram
        # cmd_id at offset 2+1+1+2 = 6
        try:
            import struct
            cmd_id = raw[6]
            param = struct.unpack_from('<i', raw, 7)[0]
        except Exception as e:
            print("Failed to parse command payload:", e)
            return
        ack_code, msg = fsm.apply_command(cmd_id, param)
        print(f"Uplink cmd received id={cmd_id} param={param} -> ack={ack_code} msg='{msg}'")
        # optional: send an ACK back as telemetry or command response (not implemented)

    # start command listener
    uplink_host = cfg.get('uplink_host', '127.0.0.1')
    uplink_port = int(cfg.get('uplink_port', 5006))
    cmd_listener = CommandListener(uplink_host, uplink_port, on_command)
    cmd_listener.start()
    print(f"Command listener started on {uplink_host}:{uplink_port}")

    seq = 0
    rate = max(50, int(cfg.get('telemetry_rate_ms', 500)))
    corrupt_prob = float(cfg.get("debug_corrupt_prob", 0.0))
    print("Starting sim -> sending to {}:{}".format(cfg.get('udp_host', '127.0.0.1'), cfg.get('udp_port', 5005)))
    try:
        while True:
            s = sim.step()
            mode = fsm.update(s)
            ts_ms = int(time.time() * 1000) & 0xFFFFFFFF
            frame = pack_telemetry(
                seq=seq,
                timestamp_ms=ts_ms,
                mode=mode,
                batt_mv=s['batt_mv'],
                temp_centideg=s['temp_centideg'],
                press_pa=s['press_pa'],
                alt_cm=s['alt_cm'],
                gyro_xyz=s['gyro'],
                acc_xyz=s['acc'],
                light=s['light']
            )

            # optional corruption (debug only)
            if corrupt_prob > 0.0 and random.random() < corrupt_prob:
                fb = bytearray(frame)
                if len(fb) > 8:
                    fb[8] ^= 0xFF
                    frame = bytes(fb)

            sender.send(frame)
            print(f"Sent seq={seq} mode={mode} batt={s['batt_mv']} temp_c={s['temp_centideg']/100:.2f}")
            seq = (seq + 1) & 0xFFFF
            time.sleep(rate / 1000.0)
    except KeyboardInterrupt:
        print("Simulator stopped")
    finally:
        cmd_listener.stop()

if __name__ == '__main__':
    main()


