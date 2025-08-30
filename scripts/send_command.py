#!/usr/bin/env python3
import socket
import struct
import sys

# default simulator uplink host/port
HOST = "127.0.0.1"
PORT = 5006

def send_command(cmd_id: int, param: int):
    # Pack command: cmd_id (1 byte) + param (4 bytes, little endian)
    payload = struct.pack('<Bi', cmd_id, param)
    
    # Simple "frame" header: preamble + version + msgtype + seq
    # For testing, seq = 0, version = 1, msgtype = 2 (CMD)
    preamble = b'\xAA\x55'
    version = b'\x01'
    msgtype = b'\x02'
    seq = struct.pack('<H', 0)
    frame = preamble + version + msgtype + seq + payload

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(frame, (HOST, PORT))
    sock.close()
    print(f"Sent command id={cmd_id} param={param} to {HOST}:{PORT}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python send_command.py <cmd_id> <param>")
        sys.exit(1)
    cmd_id = int(sys.argv[1])
    param = int(sys.argv[2])
    send_command(cmd_id, param)

