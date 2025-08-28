# ground/logger.py
import os, csv, time, json

def _update_symlink(path: str, link_path: str):
    try:
        if os.path.islink(link_path) or os.path.exists(link_path):
            os.remove(link_path)
    except Exception:
        pass
    try:
        os.symlink(os.path.basename(path), link_path)
    except Exception:
        # symlink may fail on some filesystems; ignore
        pass

class CsvLogger:
    def __init__(self, log_dir: str):
        os.makedirs(log_dir, exist_ok=True)
        ts = int(time.time())
        self.path = os.path.join(log_dir, f"telemetry_{ts}.csv")  # set path first
        self._f = open(self.path, "w", newline="")
        self._w = csv.DictWriter(self._f, fieldnames=[
            "timestamp",      # local ground timestamp
            "version",
            "msgtype",
            "seq",
            "timestamp_ms",   # satellite-side timestamp
            "mode",
            "batt_mv",
            "temp_c",
            "press_pa",
            "alt_cm",
            "gyro_x",
            "gyro_y",
            "gyro_z",
            "acc_x",
            "acc_y",
            "acc_z",
            "light",
            "comp_len",
            "raw_len",
        ])
        self._w.writeheader()
        _update_symlink(self.path, os.path.join(log_dir, "latest.csv"))

    def write(self, row: dict):
        row = dict(row)  # shallow copy
        row["timestamp"] = int(time.time())
        self._w.writerow(row)
        self._f.flush()

    def close(self):
        self._f.close()


class JsonlLogger:
    def __init__(self, log_dir: str):
        os.makedirs(log_dir, exist_ok=True)
        ts = int(time.time())
        self.path = os.path.join(log_dir, f"telemetry_{ts}.jsonl")  # set path first
        self._f = open(self.path, "w")
        _update_symlink(self.path, os.path.join(log_dir, "latest.jsonl"))

    def write(self, row: dict):
        row = dict(row)  # shallow copy
        row["timestamp"] = int(time.time())
        self._f.write(json.dumps(row) + "\n")
        self._f.flush()

    def close(self):
        self._f.close()

