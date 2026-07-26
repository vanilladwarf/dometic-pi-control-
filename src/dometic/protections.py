"""Dometic-mandated protection timers and lockouts."""
from __future__ import annotations
from dataclasses import dataclass
from dometic.config import ProtectionsCfg


@dataclass
class Protections:
    cfg: ProtectionsCfg
    _last_compressor_off: float = 0.0
    _last_heat_pump_start: float = 0.0
    _in_defrost: bool = False
    _defrost_until: float = 0.0

    def can_start_compressor(self, now: float) -> bool:
        return (now - self._last_compressor_off) >= self.cfg.min_compressor_off_secs

    def can_start_heat_pump(self, outdoor_f) -> bool:
        if outdoor_f is None:
            return True
        if outdoor_f <= self.cfg.hard_lockout_f:
            return False
        return outdoor_f > self.cfg.heat_pump_lockout_f

    def can_run_cool(self, outdoor_f) -> bool:
        if outdoor_f is None:
            return True
        return outdoor_f <= self.cfg.max_outdoor_for_cool_f

    def record_compressor_off(self, now: float):
        self._last_compressor_off = now

    def record_heat_pump_start(self, now: float):
        self._last_heat_pump_start = now

    def maybe_defrost(self, outdoor_f, now: float) -> bool:
        if self._in_defrost:
            if now >= self._defrost_until:
                self._in_defrost = False
                self._last_heat_pump_start = now + self.cfg.defrost_recovery_secs
            return False
        if (outdoor_f is not None
                and 24 < outdoor_f < 42
                and (now - self._last_heat_pump_start) > self.cfg.defrost_run_secs):
            self._in_defrost = True
            self._defrost_until = now + self.cfg.defrost_cycle_secs
            return True
        return False

    def in_defrost(self) -> bool:
        return self._in_defrost
