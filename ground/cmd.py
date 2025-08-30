# ground/cmd.py
import socket
import sys
from sat_sim.packet import make_command_frame

UPLINK_HOST = "127.0.0.1"
UPLINK_PORT = 5006   # must match the sat_sim uplink listener port

def send_command(cmd_id: int, param: int = 0):
    frame = make_command_frame(cmd_id, param)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(frame, (UPLINK_HOST, UPLINK_PORT))
    print(f"[GROUND] Sent uplink: cmd_id={cmd_id}, param={param}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m ground.cmd <cmd_id> [param]")
        sys.exit(1)

    cmd_id = int(sys.argv[1])
    param = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    send_command(cmd_id, param)

