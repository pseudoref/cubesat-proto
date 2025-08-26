# ground/receiver.py
import socket
from sat_sim.packet import unpack_frame
HOST = '127.0.0.1'
PORT = 5005

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"Listening on {HOST}:{PORT}")
    while True:
        data, addr = sock.recvfrom(4096)
        try:
            info = unpack_frame(data)
            print("RX seq:", info['seq'], "mode:", info['mode'], "temp:", info['temp_centideg']/100.0)
        except Exception as e:
            print("Bad frame:", e)

if __name__ == '__main__':
    run()

