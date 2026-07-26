"""Tests for the Thermostat hysteresis logic."""
from dometic.config import ThermostatCfg
from dometic.thermostat import Thermostat


def test_off_mode_always_off():
    t = Thermostat(ThermostatCfg())
    assert t.decide(70.0, "off") == "off"
    assert t.decide(120.0, "off") == "off"
    assert t.decide(-10.0, "off") == "off"


def test_fan_only_mode_always_fan():
    t = Thermostat(ThermostatCfg())
    assert t.decide(70.0, "fan_only") == "fan"
    assert t.decide(100.0, "fan_only") == "fan"


def test_cool_above_setpoint_demands_cool():
    t = Thermostat(ThermostatCfg(setpoint_cool_f=74, cool_deadband_f=1.5))
    assert t.decide(80.0, "cool") == "cool"
    assert t.decide(74.0, "cool") == "cool"


def test_cool_below_deadband_does_not_cool():
    t = Thermostat(ThermostatCfg(setpoint_cool_f=74, cool_deadband_f=1.5))
    assert t.decide(70.0, "cool") != "cool"
    assert t.decide(72.4, "cool") != "cool"


def test_heat_below_setpoint_demands_heat():
    t = Thermostat(ThermostatCfg(setpoint_heat_f=68, heat_deadband_f=1.5))
    assert t.decide(60.0, "heat") == "heat"
    assert t.decide(68.0, "heat") == "heat"


def test_heat_above_deadband_does_not_heat():
    t = Thermostat(ThermostatCfg(setpoint_heat_f=68, heat_deadband_f=1.5))
    assert t.decide(80.0, "heat") != "heat"
    assert t.decide(69.6, "heat") != "heat"


def test_nan_returns_off():
    t = Thermostat(ThermostatCfg())
    assert t.decide(float("nan"), "cool") == "off"
    assert t.decide(float("nan"), "heat") == "off"


def test_hysteresis_holds_in_band():
    cfg = ThermostatCfg(setpoint_cool_f=74, cool_deadband_f=1.5)
    t = Thermostat(cfg)
    d = t.decide(76.0, "cool")
    assert d == "cool"
    t.record(d)
    d = t.decide(75.0, "cool")
    assert d == "cool"
    d = t.decide(72.0, "cool")
    assert d != "cool"


def test_auto_mode_decision():
    cfg = ThermostatCfg(setpoint_cool_f=74, setpoint_heat_f=68)
    t = Thermostat(cfg)
    assert t.decide(80.0, "auto") == "cool"
    assert t.decide(60.0, "auto") == "heat"
    assert t.decide(70.0, "auto") == "off"


def test_unknown_mode_returns_off():
    t = Thermostat(ThermostatCfg())
    assert t.decide(70.0, "garbage") == "off"


def test_deterministic():
    cfg = ThermostatCfg(setpoint_cool_f=74, cool_deadband_f=1.5)
    t = Thermostat(cfg)
    for _ in range(5):
        assert t.decide(75.0, "cool") == t.decide(75.0, "cool")
