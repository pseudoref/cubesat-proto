# ground/stats.py
import time

class StatsTracker:
    def __init__(self):
        self.total_good = 0
        self.total_bad = 0
        self.last_seq = None
        self.seq_loss = 0
        self.start_time = time.time()

    def note_good(self, seq):
        self.total_good += 1
        # check for lost sequence numbers
        if self.last_seq is not None and seq > self.last_seq + 1:
            self.seq_loss += (seq - self.last_seq - 1)
        self.last_seq = seq

    def note_bad(self):
        self.total_bad += 1

    def snapshot(self):
        elapsed = time.time() - self.start_time
        rate = self.total_good / elapsed if elapsed > 0 else 0
        total = self.total_good + self.total_bad
        loss_pct = (self.seq_loss / total * 100.0) if total > 0 else 0.0
        return {
            "total_good": self.total_good,
            "total_bad": self.total_bad,
            "seq_loss": self.seq_loss,
            "loss_pct": round(loss_pct, 1),
            "rate_est_pps": round(rate, 1),
        }

