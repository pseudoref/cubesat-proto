# sat_sim/sensors.py
import time
import math
import random

class SensorSimulator:
    def __init__(self, config):
        self.t0 = time.time()
        self.batt_mv = config.get("battery_start_mv", 4200)
        self.batt_drain_mv_per_sec = config.get("battery_drain_mv_per_sec", 0.05)
        self.temp_base = config.get("temp_base_c", 25.0)
        self.press_base = config.get("pressure_base_pa", 101325)
        self._last_time = self.t0

    def step(self):
        now = time.time()
        dt = now - self._last_time
        self._last_time = now

        # battery slow drain
        self.batt_mv -= self.batt_drain_mv_per_sec * dt * 1000.0 / 1000.0

        # simple oscillating temperature (centi-deg)
        t = now - self.t0
        temp = self.temp_base + math.sin(t / 30.0) * 1.5 + random.gauss(0, 0.2)  # deg C
        temp_centideg = int(temp * 100)

        # pressure varies slightly
        press = self.press_base + math.cos(t / 45.0) * 5 + random.gauss(0, 1)

        # altitude estimate (fake) from pressure using a simple model
        # approximate: altitude in meters from standard atmosphere (not precise)
        alt_m = 44330.0 * (1.0 - (press / 101325.0) ** (1.0 / 5.255))
        alt_cm = int(alt_m * 100)

        # gyro/acc simulated (int16)
        gyro_x = int(random.gauss(0, 20))
        gyro_y = int(random.gauss(0, 20))
        gyro_z = int(random.gauss(0, 20))

        acc_x = int(random.gauss(0, 50))
        acc_y = int(random.gauss(0, 50))
        acc_z = int(random.gauss(1000, 50))  # ~1g on Z (milligravities or scaled unit)

        light = int(max(0, min(1023, 512 + math.sin(t / 10.0) * 400 + random.gauss(0, 40))))

        return {
            "batt_mv": int(max(3000, min(4200, self.batt_mv))),
            "temp_centideg": temp_centideg,
            "press_pa": int(press),
            "alt_cm": alt_cm,
            "gyro": (gyro_x, gyro_y, gyro_z),
            "acc": (acc_x, acc_y, acc_z),
            "light": light
        }

