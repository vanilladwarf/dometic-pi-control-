"""Thread-safe shared state."""
from __future__ import annotations
import threading
import time
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class RuntimeState:
    mode: str = "off"
    fan: str = "low"
    setpoint_cool_f: float = 74.0
    setpoint_heat_f: float = 68.0
    room_f: Optional[float] = None
    outdoor_f: Optional[float] = None
    last_decision: str = "off"
    in_defrost: bool = False
    compressor_active: bool = False
    last_update: float = 0.0
    error: str = ""

    def snapshot(self):
        return asdict(self)


class StateStore:
    def __init__(self):
        self._state = RuntimeState()
        self._lock = threading.RLock()

    def get(self) -> RuntimeState:
        with self._lock:
            return self._state

    def update(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                if hasattr(self._state, k):
                    setattr(self._state, k, v)
            self._state.last_update = time.time()

    def to_dict(self):
        with self._lock:
            return self._state.snapshot()


_store = StateStore()


def get_store() -> StateStore:
    return _store
