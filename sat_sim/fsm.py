# sat_sim/fsm.py
class CubeSatFSM:
    MODE_OPERATIONAL = 0
    MODE_SAFE = 1
    MODE_IDLE = 2
    CMD_SET_MODE = 1
    CMD_RESET_SEQ = 2
    CMD_PING = 3

    def apply_command(self, cmd_id: int, param: int = 0):
    """
    Handle received uplink commands. Return a tuple (ack_code, message).
    ack_code: 0 = OK, 1 = UNKNOWN_CMD, 2 = BAD_PARAM
    """
    if cmd_id == self.CMD_SET_MODE:
        if param in (self.MODE_OPERATIONAL, self.MODE_SAFE, self.MODE_IDLE):
            self.mode = param
            return 0, f"Mode set to {self.mode}"
        return 2, "Invalid mode param"
    elif cmd_id == self.CMD_RESET_SEQ:
        # No seq state inside FSM — main sim can reset its seq if required.
        return 0, "Reset seq not handled here"
    elif cmd_id == self.CMD_PING:
        return 0, "PONG"
    else:
        return 1, "Unknown command"

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

