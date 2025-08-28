# tools/plot_from_log.py
import os, sys, json, csv
import matplotlib.pyplot as plt

def load_jsonl(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows

def load_csv(path):
    rows = []
    with open(path, "r") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({k: (float(v) if v.replace('.','',1).isdigit() else v) for k, v in row.items()})
    return rows

def main(path):
    if path.endswith(".jsonl"):
        rows = load_jsonl(path)
    elif path.endswith(".csv"):
        rows = load_csv(path)
    else:
        print("Give a .jsonl or .csv file")
        sys.exit(1)

    if not rows:
        print("No data")
        sys.exit(1)

    t = [r.get("timestamp", 0) for r in rows]
    temp = [r.get("temp_c", 0) for r in rows]
    batt = [r.get("batt_mv", 0) for r in rows]
    alt  = [ (r.get("alt_cm", 0) or 0)/100.0 for r in rows]

    # temp
    plt.figure()
    plt.plot(t, temp)
    plt.xlabel("time (s)")
    plt.ylabel("temperature (°C)")
    plt.title("Temperature vs Time")
    plt.savefig("plot_temp.png", dpi=150)

    # battery
    plt.figure()
    plt.plot(t, batt)
    plt.xlabel("time (s)")
    plt.ylabel("battery (mV)")
    plt.title("Battery vs Time")
    plt.savefig("plot_batt.png", dpi=150)

    # altitude
    plt.figure()
    plt.plot(t, alt)
    plt.xlabel("time (s)")
    plt.ylabel("altitude (m)")
    plt.title("Altitude vs Time")
    plt.savefig("plot_alt.png", dpi=150)

    print("Saved: plot_temp.png, plot_batt.png, plot_alt.png")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/plot_from_log.py ground/logs/latest.jsonl")
        sys.exit(1)
    main(sys.argv[1])

