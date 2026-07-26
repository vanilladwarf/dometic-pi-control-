"""Sensor drivers: BME280 (I2C) and DS18B20 (1-Wire).
On non-Pi systems, returns None to let the daemon run in test mode."""
from __future__ import annotations
import glob
import os
from typing import Optional


def _read_ds18b20_c(sensor_id: str = "") -> Optional[float]:
    base = "/sys/bus/w1/devices"
    if not os.path.isdir(base):
        return None
    paths = ([f"{base}/{sensor_id}/w1_slave"] if sensor_id
             else glob.glob(f"{base}/28-*/w1_slave"))
    for p in paths:
        try:
            with open(p) as f:
                lines = f.readlines()
            if len(lines) < 2 or lines[0].strip()[-3:] != "YES":
                continue
            t = lines[1].split("t=", 1)[1].strip()
            return int(t) / 1000.0
        except (FileNotFoundError, IndexError, ValueError):
            continue
    return None


def read_room_f(cfg) -> Optional[float]:
    if cfg.sensors.room == "ds18b20":
        c = _read_ds18b20_c(cfg.sensors.ds18b20_id)
    else:
        try:
            import smbus2
            import bme280
            bus = smbus2.SMBus(cfg.sensors.bme280_bus)
            calib = bme280.load_calibration_params(
                bus, cfg.sensors.bme280_address)
            data = bme280.sample(bus, cfg.sensors.bme280_address, calib)
            return data.temperature
        except Exception:
            return None
    if c is None:
        return None
    return c * 9.0 / 5.0 + 32.0


def read_outdoor_f(cfg) -> Optional[float]:
    c = _read_ds18b20_c(cfg.sensors.ds18b20_id)
    if c is None:
        return None
    return c * 9.0 / 5.0 + 32.0
