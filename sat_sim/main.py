# sat_sim/main.py
import time
import json
import os
from .sensors import SensorSimulator
from .packet import pack_telemetry
from .link import UDPSender
from .fsm import CubeSatFSM

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def main():
    cfg = load_config()
    sim = SensorSimulator(cfg)
    fsm = CubeSatFSM(temp_high_centi=4000, batt_low_mv=3300)
    sender = UDPSender(cfg['udp_host'], cfg['udp_port'])

    seq = 0
    rate = max(50, int(cfg.get('telemetry_rate_ms', 500)))
    print("Starting sim -> sending to {}:{}".format(cfg['udp_host'], cfg['udp_port']))
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
            sender.send(frame)
            print(f"Sent seq={seq} mode={mode} batt={s['batt_mv']} temp_c={s['temp_centideg']/100:.2f}")
            seq = (seq + 1) & 0xFFFF
            time.sleep(rate / 1000.0)
    except KeyboardInterrupt:
        print("Simulator stopped")

if __name__ == '__main__':
    main()

