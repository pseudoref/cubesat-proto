# ground/command_sender.py
import json
import struct
import time
import argparse
from sat_sim.packet import pack_command
from sat_sim.link import UDPSender

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5006)
    args = parser.parse_args()

    sender = UDPSender(args.host, args.port)
    seq = 0
    print(f"Command sender ready -> {args.host}:{args.port}")
    print("Commands:")
    print("  1) setmode <0|1|2>     -- 0=OP,1=SAFE,2=IDLE")
    print("  2) resetseq            -- reset seq (sim only prints ack)")
    print("  3) ping                -- test uplink")
    print("  q) quit")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()
        if cmd in ("q", "quit", "exit"):
            break
        if cmd == "setmode" and len(parts) == 2:
            try:
                mode = int(parts[1])
            except:
                print("bad mode")
                continue
            frame = pack_command(cmd_id=1, param=mode, seq=seq)
            sender.send(frame)
            print(f"Sent SET_MODE={mode} seq={seq}")
        elif cmd == "resetseq":
            frame = pack_command(cmd_id=2, param=0, seq=seq)
            sender.send(frame)
            print(f"Sent RESET_SEQ seq={seq}")
        elif cmd == "ping":
            frame = pack_command(cmd_id=3, param=0, seq=seq)
            sender.send(frame)
            print(f"Sent PING seq={seq}")
        else:
            print("Unknown command")
        seq = (seq + 1) & 0xFFFF

if __name__ == "__main__":
    main()

