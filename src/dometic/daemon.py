"""Main control loop."""
from __future__ import annotations
import logging
import signal
import threading
import time
from dometic.config import load_config
from dometic.logging_setup import setup_logging
from dometic.relays import get_board
from dometic.sensors import read_room_f, read_outdoor_f
from dometic.protections import Protections
from dometic.thermostat import Thermostat
from dometic.state import get_store

log = logging.getLogger("dometic.daemon")
_shutdown = threading.Event()


def _install_signals():
    def handler(signum, _frame):
        log.info("Received signal %s", signum)
        _shutdown.set()
    try:
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    except ValueError:
        pass  # not main thread


def _apply_decision(board, decision, fan, prot, now):
    if decision == "off":
        board.all_off()
    elif decision == "fan":
        if fan == "high":
            board.set_state(FAN_HIGH=True, FAN_LOW=False)
        else:
            board.set_state(FAN_LOW=True, FAN_HIGH=False)
    elif decision == "cool":
        if not prot.can_start_compressor(now):
            board.set_state(FAN_LOW=(fan != "high"), FAN_HIGH=(fan == "high"))
        elif fan == "high":
            board.set_state(FAN_LOW=False, FAN_HIGH=True, COOL=True)
        else:
            board.set_state(FAN_LOW=True, FAN_HIGH=False, COOL=True)
    elif decision == "heat":
        if not prot.can_start_compressor(now):
            board.set_state(FAN_LOW=(fan != "high"), FAN_HIGH=(fan == "high"))
        elif fan == "high":
            board.set_state(FAN_LOW=False, FAN_HIGH=True,
                            HEAT_PUMP=True, COMP1=True, RV1=True)
        else:
            board.set_state(FAN_LOW=True, FAN_HIGH=False,
                            HEAT_PUMP=True, COMP1=True, RV1=True)


def run():
    log = setup_logging()
    log.info("Dometic 39424.602 control daemon starting")
    _install_signals()
    cfg = load_config()
    board = get_board(cfg)
    board.setup()
    prot = Protections(cfg.protections)
    thermo = Thermostat(cfg.thermostat)
    store = get_store()
    store.update(mode=cfg.thermostat.default_mode,
                 fan=cfg.thermostat.default_fan,
                 setpoint_cool_f=cfg.thermostat.setpoint_cool_f,
                 setpoint_heat_f=cfg.thermostat.setpoint_heat_f)
    compressor_was_on = False
    last_log = 0.0
    try:
        while not _shutdown.is_set():
            now = time.time()
            try:
                cfg = load_config()
            except Exception as e:
                log.warning("config reload failed: %s", e)
            state = store.get()
            room = read_room_f(cfg)
            out = read_outdoor_f(cfg)
            decision = thermo.decide(room, state.mode)
            thermo.record(decision)
            if decision == "heat" and not prot.can_start_heat_pump(out):
                decision = "off"
            if decision == "cool" and not prot.can_run_cool(out):
                decision = "fan"
            _apply_decision(board, decision, state.fan, prot, now)
            comp_on = decision in ("cool", "heat")
            if compressor_was_on and not comp_on:
                prot.record_compressor_off(now)
            if not compressor_was_on and comp_on:
                prot.record_heat_pump_start(now)
            compressor_was_on = comp_on
            store.update(room_f=room, outdoor_f=out, last_decision=decision,
                         compressor_active=comp_on)
            if now - last_log >= cfg.loop.log_interval_secs:
                last_log = now
                log.info("room=%s outdoor=%s mode=%s decision=%s",
                         room, out, state.mode, decision)
            for _ in range(int(cfg.loop.period_secs * 10)):
                if _shutdown.is_set():
                    break
                time.sleep(0.1)
    finally:
        log.info("Cleaning up relays")
        board.cleanup()


if __name__ == "__main__":
    run()
