# ground/dashboard_tui.py
import os, json, time, curses, statistics
from collections import deque
from .tail import tail_lines

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LATEST = os.path.join(LOG_DIR, "latest.jsonl")

FIELDS = [
    "version","msgtype","seq","timestamp_ms","mode",
    "batt_mv","temp_c","press_pa","alt_cm","light",
    "gyro_x","gyro_y","gyro_z","acc_x","acc_y","acc_z",
    "comp_len","raw_len","timestamp"
]

def find_log():
    if os.path.exists(LATEST):
        return LATEST
    # fallback: pick newest .jsonl
    cands = [os.path.join(LOG_DIR, f) for f in os.listdir(LOG_DIR) if f.endswith(".jsonl")]
    if not cands:
        return None
    return max(cands, key=os.path.getmtime)

def draw_bar(win, y, x, label, value, minv, maxv, width=40):
    v = max(minv, min(maxv, value))
    frac = 0.0 if maxv == minv else (v - minv) / (maxv - minv)
    filled = int(frac * width)
    bar = "[" + ("#" * filled) + ("-" * (width - filled)) + "]"
    win.addstr(y, x, f"{label:<12} {bar} {value}")

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    path = find_log()
    if not path:
        stdscr.addstr(0, 0, "No JSONL log found. Start ground station first, then run dashboard.")
        stdscr.refresh()
        time.sleep(3)
        return

    # rate calc over last N seconds using ground-side timestamps
    recent_ts = deque(maxlen=1000)
    recent_seq = deque(maxlen=1000)

    # last values
    last = {k: None for k in FIELDS}
    last_time = time.time()

    stdscr.addstr(0, 0, f"Live Telemetry Dashboard  (source: {os.path.basename(path)})   Press 'q' to quit")
    stdscr.refresh()

    row_y = 2
    for line in tail_lines(path):
        try:
            row = json.loads(line)
        except Exception:
            continue

        # update state
        for k in FIELDS:
            if k in row:
                last[k] = row[k]

        # update rate stats
        if "timestamp" in row:
            recent_ts.append(row["timestamp"])
        if "seq" in row:
            recent_seq.append(row["seq"])

        # draw UI at ~10 Hz
        now = time.time()
        if now - last_time < 0.1:
            # still allow quit
            ch = stdscr.getch()
            if ch in (ord('q'), ord('Q')):
                break
            continue
        last_time = now

        stdscr.erase()
        stdscr.addstr(0, 0, f"Live Telemetry Dashboard  (source: {os.path.basename(path)})   Press 'q' to quit")

        # compute pps over ~10s window
        pps = 0.0
        if len(recent_ts) >= 2:
            dt = recent_ts[-1] - recent_ts[0]
            if dt > 0:
                pps = (len(recent_ts) - 1) / dt

        # header line
        stdscr.addstr(2, 0, f"pps≈{pps:.2f}   seq={last.get('seq')}   mode={last.get('mode')}   "
                             f"ver={last.get('version')} type={last.get('msgtype')}")

        # main metrics
        y = 4
        try:
            temp_c = float(last.get("temp_c") or 0.0)
            batt_mv = int(last.get("batt_mv") or 0)
            alt_cm = int(last.get("alt_cm") or 0)
            light = int(last.get("light") or 0)
        except Exception:
            temp_c, batt_mv, alt_cm, light = 0.0, 0, 0, 0

        draw_bar(stdscr, y+0, 0, "Temp (°C)", temp_c, -20, 80)
        draw_bar(stdscr, y+1, 0, "Batt (mV)", batt_mv, 3000, 4200)
        draw_bar(stdscr, y+2, 0, "Alt (m)",  alt_cm/100.0, 0, 5000)
        draw_bar(stdscr, y+3, 0, "Light",    light, 0, 4095)

        # IMU snapshot
        gx = last.get("gyro_x"); gy = last.get("gyro_y"); gz = last.get("gyro_z")
        ax = last.get("acc_x");  ay = last.get("acc_y");  az = last.get("acc_z")
        stdscr.addstr(y+5, 0, f"Gyro: {gx} {gy} {gz}     Acc: {ax} {ay} {az}")

        # timestamps
        stdscr.addstr(y+7, 0, f"Sat ts (ms): {last.get('timestamp_ms')}    Ground ts: {last.get('timestamp')}")

        stdscr.refresh()

        # quit?
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q')):
            break

if __name__ == "__main__":
    curses.wrapper(main)

