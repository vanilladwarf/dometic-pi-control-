"""Tests for the StateStore."""
from dometic.state import StateStore, get_store


def test_state_store_update():
    s = StateStore()
    s.update(mode="cool", fan="high")
    snap = s.snapshot()
    assert snap["mode"] == "cool"
    assert snap["fan"] == "high"


def test_singleton():
    assert get_store() is get_store()


def test_initial_state():
    s = StateStore()
    snap = s.snapshot()
    assert snap["mode"] == "off"
    assert snap["fan"] == "low"
    assert 40 <= snap["setpoint_cool_f"] <= 99
    assert 40 <= snap["setpoint_heat_f"] <= 99


def test_unknown_attrs_ignored():
    s = StateStore()
    before = s.to_dict()
    s.update(nonexistent_attr="should be ignored")
    after = s.to_dict()
    assert before == after
