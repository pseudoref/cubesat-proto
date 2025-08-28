# ground/receiver.py (diagnostic)
import socket
import csv
import time
from sat_sim.packet import unpack_frame

HOST = '127.0.0.1'
PORT = 5005
LOG_FILE = "telemetry_log.csv"

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[GROUND] Listening on {HOST}:{PORT}")

    # open CSV file for logging
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "seq", "mode", "batt_mv", "temp_c", "press_pa", "alt_m", "light"])

        while True:
            data, addr = sock.recvfrom(4096)
            try:
                info = unpack_frame(data)

                # convert units
                temp_c = info['temp_centideg'] / 100.0
                alt_m = info['alt_cm'] / 100.0

                # print a nicely formatted line
                print(f"RX seq={info['seq']:5d}  mode={info['mode']:2d}  "
                      f"batt={info['batt_mv']:4d} mV  temp={temp_c:6.2f} °C  "
                      f"alt={alt_m:7.2f} m  light={info['light']:4d}")

                # log to CSV
                writer.writerow([
                    int(time.time()), info['seq'], info['mode'],
                    info['batt_mv'], temp_c, info['press_pa'],
                    alt_m, info['light']
                ])
                f.flush()  # ensure data is saved

            except Exception as e:
                # DIAGNOSTIC: print debug info about the raw datagram
                print("[GROUND] Bad frame:", e)
                print("[GROUND] datagram len:", len(data))
                # print at most first 200 chars of hex so it's readable
                hexdump = data.hex()
                print("[GROUND] datagram hex (start..):", hexdump[:200])
                # optional: write the first few bad frames to files for deeper analysis
                ts = int(time.time())
                try:
                    with open(f"ground/badframe_{ts}.bin", "wb") as bf:
                        bf.write(data)
                except Exception:
                    pass

if __name__ == '__main__':
    run()


