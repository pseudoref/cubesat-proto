# ground/ground.py
import os, json, socket, time
from typing import Optional
from .decode import decode_datagram
from .logger import CsvLogger, JsonlLogger
from .stats import StatsTracker

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def run():
    cfg = load_config()
    host = cfg.get("udp_host", "127.0.0.1")
    port = int(cfg.get("udp_port", 5005))
    log_dir = cfg.get("ground_log_dir", "ground/logs")
    status_iv = int(cfg.get("ground_status_interval_sec", 5))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(0.5)

    csv = CsvLogger(log_dir) if cfg.get("ground_log_csv", True) else None
    jsonl = JsonlLogger(log_dir) if cfg.get("ground_log_jsonl", True) else None
    stats = StatsTracker()

    print(f"Ground station listening on {host}:{port}")
    last_status = time.time()

    try:
        while True:
            try:
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                # periodic status even if quiet
                pass
            else:
                try:
                    row = decode_datagram(data)   # may raise ValueError
                except Exception as e:
                    print("[GROUND] Decode failed:", e)   # debug info
                    stats.note_bad()
                else:
                    stats.note_good(row["seq"])
                    if csv: csv.write(row)
                    if jsonl: jsonl.write(row)

            # Print periodic status
            if time.time() - last_status >= status_iv:
                snap = stats.snapshot()
                print(f"[status] good={snap['total_good']} bad={snap['total_bad']} "
                      f"loss={snap['seq_loss']} ({snap['loss_pct']}%) rate≈{snap['rate_est_pps']} pps")
                last_status = time.time()

    except KeyboardInterrupt:
        print("Ground station stopped.")
    finally:
        if csv: csv.close()
        if jsonl: jsonl.close()

if __name__ == "__main__":
    run()

