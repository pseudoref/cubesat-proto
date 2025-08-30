# sat_sim/command_listener.py
import socket
import threading
import time
from typing import Callable

MIN_CMD_FRAME_SIZE = 10  # minimum valid command frame length in bytes

class CommandListener:
    """
    Listens on UDP port for command frames (binary) and calls callback with (cmd_id, param, seq, raw_data).
    Non-blocking loop in a thread.
    """
    def __init__(self, host: str, port: int, callback: Callable):
        self.host = host
        self.port = int(port)
        self.callback = callback
        self._sock = None
        self._thread = None
        self._stop = threading.Event()

    def start(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # allow reuse in local tests
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.settimeout(0.5)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            try:
                data, addr = self._sock.recvfrom(1024)
            except Exception:
                continue

            if len(data) < MIN_CMD_FRAME_SIZE:
                # ignore too-short frames
                print(f"[CMD LISTENER] Ignored frame too short ({len(data)} bytes)")
                continue

            try:
                # Expect caller to parse bytes (we keep listener simple)
                # The callback should handle parsing (using sat_sim.packet.unpack_frame)
                self.callback(data, addr)
            except Exception:
                # swallow callback errors but print to console
                print("[CMD LISTENER] Command callback error")
                continue

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        try:
            if self._sock:
                self._sock.close()
        except Exception:
            pass

