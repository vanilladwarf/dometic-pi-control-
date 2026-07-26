"""Integration test: the daemon's main loop runs end-to-end with
mocked GPIO and sensors, and the relay state matches the decision."""
import time
import pytest
from unittest.mock import patch

from dometic.config import Config
from dometic.state import get_store
from dometic.relays import get_board
from dometic.thermostat import Thermostat
from dometic.protections import Protections
import dometic.daemon as daemon
import dometic.relays as relays_mod


class FakeGPIO:
    BCM = 11
    OUT = 0
    IN = 1
    HIGH = 1
    LOW = 0
    BOARD = None
    def __init__(self):
        self.mode = None
        self.pin_mode = {}
        self.pin_state = {}
        self.events = []
    def setmode(self, mode): self.mode = mode
    def setwarnings(self, flag): pass
    def setup(self, pin, direction, initial=None):
        self.pin_mode[pin] = direction
        if initial is not None:
            self.pin_state[pin] = initial
    def output(self, pin, value):
        self.pin_state[pin] = value
        self.events.append(("output", pin, value))
    def input(self, pin):
        return self.pin_state.get(pin, 1)
    def cleanup(self):
        self.pin_state.clear()


@pytest.fixture
def fake_gpio(monkeypatch):
    fake = FakeGPIO()
    fake.BOARD = fake
    monkeypatch.setattr("dometic.relays.GPIO", fake)
    monkeypatch.setattr("dometic.daemon.GPIO", fake)
    relays_mod._board = None
    yield fake
    relays_mod._board = None


def test_cool_mode_energises_fan_and_cool(fake_gpio):
    cfg = Config()
    board = get_board(cfg)
    board.setup()
    get_store().update(mode="cool", fan="low")
    prot = Protections(cfg.protections)
    prot._last_compressor_off = 0
    daemon._apply_decision(board, "cool", "low", prot, time.time())
    assert fake_gpio.pin_state[17] == 0   # FAN_LOW active
    assert fake_gpio.pin_state[22] == 0   # COOL active
    assert fake_gpio.pin_state[27] == 1   # FAN_HIGH off
    assert fake_gpio.pin_state[23] == 1   # HEAT_PUMP off


def test_heat_mode_energises_heat_pump_relay_and_ssr(fake_gpio):
    cfg = Config()
    board = get_board(cfg)
    board.setup()
    get_store().update(mode="heat", fan="low")
    prot = Protections(cfg.protections)
    prot._last_compressor_off = 0
    daemon._apply_decision(board, "heat", "low", prot, time.time())
    assert fake_gpio.pin_state[17] == 0   # FAN_LOW
    assert fake_gpio.pin_state[23] == 0   # HEAT_PUMP relay
    assert fake_gpio.pin_state[5] == 0    # COMP1 SSR
    assert fake_gpio.pin_state[13] == 0   # RV1 SSR
    assert fake_gpio.pin_state[22] == 1   # COOL off


def test_fan_only_keeps_compressor_off(fake_gpio):
    cfg = Config()
    board = get_board(cfg)
    board.setup()
    get_store().update(mode="fan_only", fan="low")
    prot = Protections(cfg.protections)
    daemon._apply_decision(board, "fan", "low", prot, time.time())
    assert fake_gpio.pin_state[17] == 0   # FAN_LOW
    assert fake_gpio.pin_state[22] == 1   # COOL off
    assert fake_gpio.pin_state[5] == 1    # COMP1 off


def test_off_mode_releases_all(fake_gpio):
    cfg = Config()
    board = get_board(cfg)
    board.setup()
    # Pre-energise everything
    for p in [17, 27, 22, 23, 5, 13]:
        fake_gpio.pin_state[p] = 0
    get_store().update(mode="off", fan="low")
    prot = Protections(cfg.protections)
    daemon._apply_decision(board, "off", "low", prot, time.time())
    for p in [17, 27, 22, 23, 5, 13]:
        assert fake_gpio.pin_state[p] == 1, f"GPIO {p} still on after off"


def test_compressor_cooldown_blocks_start(fake_gpio):
    cfg = Config()
    board = get_board(cfg)
    board.setup()
    get_store().update(mode="cool", fan="low")
    prot = Protections(cfg.protections)
    prot.record_compressor_off(time.time())
    daemon._apply_decision(board, "cool", "low", prot, time.time())
    # Compressor should be off (just fan)
    assert fake_gpio.pin_state[22] == 1
    assert fake_gpio.pin_state[17] == 0  # fan still on
