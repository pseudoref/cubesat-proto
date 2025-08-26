# sat_sim/fsm.py
class CubeSatFSM:
    MODE_OPERATIONAL = 0
    MODE_SAFE = 1
    MODE_IDLE = 2

    def __init__(self, temp_high_centi=4000, batt_low_mv=3300):
        self.mode = self.MODE_OPERATIONAL
        self.temp_high = temp_high_centi
        self.batt_low = batt_low_mv

    def update(self, sensor_snapshot: dict):
        """
        sensor_snapshot contains 'temp_centideg' and 'batt_mv'
        """
        if sensor_snapshot["temp_centideg"] > self.temp_high or sensor_snapshot["batt_mv"] < self.batt_low:
            self.mode = self.MODE_SAFE
        else:
            if self.mode == self.MODE_SAFE:
                # simple heuristic: exit safe if back to normal
                if sensor_snapshot["temp_centideg"] < (self.temp_high - 200) and sensor_snapshot["batt_mv"] > (self.batt_low + 50):
                    self.mode = self.MODE_OPERATIONAL
            else:
                self.mode = self.MODE_OPERATIONAL

        return self.mode

