"""Hysteresis thermostat with separate deadbands for cool and heat."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from dometic.config import ThermostatCfg

Decision = Literal["off", "cool", "heat", "fan"]


@dataclass
class Thermostat:
    cfg: ThermostatCfg
    _last: Decision = "off"

    def decide(self, room_f, mode: str) -> Decision:
        if room_f is None:
            return "off"
        m = (mode or self.cfg.default_mode).lower()
        if m == "off":
            return "off"
        if m == "fan_only":
            return "fan"
        if m == "cool":
            if room_f >= self.cfg.setpoint_cool_f:
                return "cool"
            if room_f <= self.cfg.setpoint_cool_f - self.cfg.cool_deadband_f:
                return "fan"
            return self._last if self._last in ("cool", "fan") else "off"
        if m == "heat":
            if room_f <= self.cfg.setpoint_heat_f:
                return "heat"
            if room_f >= self.cfg.setpoint_heat_f + self.cfg.heat_deadband_f:
                return "fan"
            return self._last if self._last in ("heat", "fan") else "off"
        if m == "auto":
            if room_f >= self.cfg.setpoint_cool_f + 1.0:
                return "cool"
            if room_f <= self.cfg.setpoint_heat_f - 1.0:
                return "heat"
            return "off"
        return "off"

    def record(self, decision: Decision):
        self._last = decision
