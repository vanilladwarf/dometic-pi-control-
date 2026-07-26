"""Tests for the Protections class."""
from dometic.config import ProtectionsCfg
from dometic.protections import Protections


def test_compressor_cooldown():
    p = Protections(ProtectionsCfg(min_compressor_off_secs=120))
    p._last_compressor_off = 1000.0
    assert not p.can_start_compressor(1050.0)
    assert not p.can_start_compressor(1119.0)
    assert p.can_start_compressor(1120.0)


def test_compressor_cooldown_resets_after_record():
    p = Protections(ProtectionsCfg(min_compressor_off_secs=10))
    p._last_compressor_off = 0.0
    p.record_compressor_off(50.0)
    assert p._last_compressor_off == 50.0
    assert not p.can_start_compressor(55.0)
    assert p.can_start_compressor(60.0)


def test_heat_pump_lockout():
    p = Protections(ProtectionsCfg(heat_pump_lockout_f=24, hard_lockout_f=10))
    assert not p.can_start_heat_pump(20.0)
    assert not p.can_start_heat_pump(10.0)
    assert not p.can_start_heat_pump(5.0)
    assert p.can_start_heat_pump(25.0)
    assert p.can_start_heat_pump(30.0)


def test_heat_pump_lockout_none_temp_allowed():
    p = Protections(ProtectionsCfg(heat_pump_lockout_f=24))
    assert p.can_start_heat_pump(None)


def test_cool_lockout():
    p = Protections(ProtectionsCfg(max_outdoor_for_cool_f=110))
    assert p.can_run_cool(80.0)
    assert p.can_run_cool(110.0)
    assert not p.can_run_cool(120.0)


def test_defrost_window():
    p = Protections(ProtectionsCfg(
        defrost_run_secs=10, defrost_cycle_secs=5, defrost_recovery_secs=1))
    p._last_heat_pump_start = 0.0
    assert p.maybe_defrost(30.0, 100.0) is True
    assert p.in_defrost()
    assert p.maybe_defrost(30.0, 103.0) is False
    assert p.maybe_defrost(30.0, 200.0) is False
    assert not p.in_defrost()


def test_defrost_only_in_window():
    p = Protections(ProtectionsCfg(defrost_run_secs=1))
    p._last_heat_pump_start = 0.0
    assert p.maybe_defrost(50.0, 100.0) is False
    assert p.maybe_defrost(20.0, 100.0) is False
    assert p.maybe_defrost(35.0, 100.0) is True
