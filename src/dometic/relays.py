"""GPIO and relay control. Falls back to a no-op stub when RPi.GPIO
is not importable (e.g. on a developer laptop running tests)."""
from __future__ import annotations
from dometic.pins import get_pin_map
from dometic.config import Config

try:
    import RPi.GPIO as GPIO
    ON = GPIO.LOW
    OFF = GPIO.HIGH
    HAVE_GPIO = True
except ImportError:
    ON = 0
    OFF = 1
    HAVE_GPIO = False


class RelayBoard:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.pins = get_pin_map(cfg)
        self._initialized = False

    def setup(self):
        if self._initialized or not HAVE_GPIO:
            return
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for p in self.pins.values():
            GPIO.setup(p, GPIO.OUT, initial=OFF)
        self._initialized = True

    def cleanup(self):
        if not self._initialized or not HAVE_GPIO:
            return
        try:
            self.all_off()
            GPIO.cleanup()
        except Exception:
            pass
        self._initialized = False

    def all_off(self):
        self.set_state()

    def set_state(self, **kwargs):
        for name, p in self.pins.items():
            if not HAVE_GPIO:
                continue
            try:
                GPIO.output(p, ON if kwargs.get(name, False) else OFF)
            except Exception:
                pass

    def snapshot(self) -> dict:
        if not HAVE_GPIO:
            return {n: False for n in self.pins}
        return {n: GPIO.input(p) == ON for n, p in self.pins.items()}


_board: RelayBoard | None = None


def get_board(cfg: Config | None = None) -> RelayBoard:
    global _board
    if _board is None:
        _board = RelayBoard(cfg)
    return _board
