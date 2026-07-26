"""End-to-end test: a complete 'call for cool' session works
through the full state -> decision -> relay path."""
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
        self.pin_state = {}
        self.events = []
    def setmode(self, mode): pass
    def setwarnings(self, flag): pass
    def setup(self, pin, direction, initial=None):
        if initial is not None:
            self.pin_state[pin] = initial
    def output(self, pin, value):
        self.pin_state[pin] = value
        self.events.append((pin, value))
    def input(self, pin):
        return self.pin_state.get(pin, 1)
    def cleanup(self): self.pin_state.clear()


@pytest.fixture
def fake_gpio(monkeypatch):
    fake = FakeGPIO()
    fake.BOARD = fake
    monkeypatch.setattr("dometic.relays.GPIO", fake)
    monkeypatch.setattr("dometic.daemon.GPIO", fake)
    relays_mod._board = None
    yield fake
    relays_mod._board = None


def test_cool_session_compressor_starts(fake_gpio):
    """Room above setpoint -> cool -> compressor runs."""
    cfg = Config()
    board = get_board(cfg)
    board.setup()
    get_store().update(mode="cool", fan="low")
    prot = Protections(cfg.protections)
    prot._last_compressor_off = 0
    thermo = Thermostat(cfg.thermostat)
    room = 80.0
    for _ in range(3):
        decision = thermo.decide(room, "cool")
        thermo.record(decision)
        daemon._apply_decision(board, decision, "low", prot, time.time())
        # Update simulated room
        room -= 0.1
    assert fake_gpio.pin_state[17] == 0   # FAN_LOW
    assert fake_gpio.pin_state[22] == 0   # COOL
    assert fake_gpio.pin_state[5] == 0    # COMP1


def test_heat_pump_session(fake_gpio):
    """Below heat setpoint -> heat -> compressor + RV on."""
    cfg = Config()
    board = get_board(cfg)
    board.setup()
    get_store().update(mode="heat", fan="low")
    prot = Protections(cfg.protections)
    prot._last_compressor_off = 0
    thermo = Thermostat(cfg.thermostat)
    room = 60.0
    for _ in range(3):
        decision = thermo.decide(room, "heat")
        thermo.record(decision)
        daemon._apply_decision(board, decision, "low", prot, time.time())
        room += 0.1
    assert fake_gpio.pin_state[17] == 0   # FAN_LOW
    assert fake_gpio.pin_state[23] == 0   # HEAT_PUMP
    assert fake_gpio.pin_state[5] == 0    # COMP1
    assert fake_gpio.pin_state[13] == 0   # RV1
    assert fake_gpio.pin_state[22] == 1   # COOL off


def test_state_transitions_off_to_cool_to_off(fake_gpio):
    """A full state machine walk through off -> cool -> off."""
    cfg = Config()
    board = get_board(cfg)
    board.setup()
    store = get_store()
    store.update(mode="off", fan="low")
    prot = Protections(cfg.protections)
    thermo = Thermostat(cfg.thermostat)
    prot._last_compressor_off = 0

    # Start in off: no relays
    decision = thermo.decide(72.0, "off")
    thermo.record(decision)
    daemon._apply_decision(board, decision, "low", prot, time.time())
    assert all(fake_gpio.pin_state.get(p, 1) == 1
               for p in [17, 22, 23])

    # Switch to cool: relays should energize
    store.update(mode="cool")
    decision = thermo.decide(80.0, "cool")
    thermo.record(decision)
    daemon._apply_decision(board, decision, "low", prot, time.time())
    assert fake_gpio.pin_state[17] == 0
    assert fake_gpio.pin_state[22] == 0

    # Back to off
    store.update(mode="off")
    decision = thermo.decide(80.0, "off")
    thermo.record(decision)
    daemon._apply_decision(board, decision, "low", prot, time.time())
    assert all(fake_gpio.pin_state.get(p, 1) == 1
               for p in [17, 22, 23])
