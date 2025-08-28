# ground/tail.py
import time
from typing import Iterator

def tail_lines(path: str) -> Iterator[str]:
    """Follow a file and yield new complete lines as they appear."""
    with open(path, "r") as f:
        # start at end
        f.seek(0, 2)
        buf = ""
        while True:
            chunk = f.read()
            if not chunk:
                time.sleep(0.2)
                continue
            buf += chunk
            while True:
                nl = buf.find("\n")
                if nl == -1:
                    break
                line = buf[:nl]
                buf = buf[nl+1:]
                if line.strip():
                    yield line

