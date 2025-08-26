# sat_sim/link.py
import socket

class UDPSender:
    def __init__(self, host='127.0.0.1', port=5005):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: bytes):
        self.sock.sendto(data, (self.host, self.port))

