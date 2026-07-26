"""Configuration loader with hot-reload support."""
from __future__ import annotations
from pathlib import Path
from typing import Literal
from dataclasses import dataclass, field
import os
import yaml


def _default_config_path() -> Path:
    env = os.environ.get("DOMETIC_CONFIG")
    if env:
        return Path(env)
    for p in (
        Path("/opt/dometic/config/config.yaml"),
        Path.cwd() / "config" / "config.yaml",
        Path(__file__).parent.parent.parent / "config" / "config.yaml",
    ):
        if p.exists():
            return p
    raise FileNotFoundError("No config.yaml found")


@dataclass
class ThermostatCfg:
    setpoint_cool_f: float = 74.0
    setpoint_heat_f: float = 68.0
    cool_deadband_f: float = 1.5
    heat_deadband_f: float = 1.5
    default_mode: str = "off"
    default_fan: str = "low"


@dataclass
class ProtectionsCfg:
    min_compressor_off_secs: int = 120
    interstage_delay_secs: int = 30
    defrost_run_secs: int = 2400
    defrost_cycle_secs: int = 270
    defrost_recovery_secs: int = 30
    heat_pump_lockout_f: float = 24.0
    hard_lockout_f: float = 10.0
    max_outdoor_for_cool_f: float = 110.0


@dataclass
class SensorsCfg:
    room: str = "bme280"
    outdoor: str = "ds18b20"
    bme280_address: int = 0x76
    bme280_bus: int = 1
    ds18b20_id: str = ""


@dataclass
class PinsCfg:
    fan_low: int = 17
    fan_high: int = 27
    cool: int = 22
    heat_pump: int = 23
    furnace: int = 24
    comp1: int = 5
    comp2: int = 6
    rv1: int = 13
    rv2: int = 19
    interstage: int = 26
    spare1: int = 16
    spare2: int = 20


@dataclass
class ApiCfg:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass
class LoopCfg:
    period_secs: float = 5.0
    log_interval_secs: int = 30


@dataclass
class MqttCfg:
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 1883
    base_topic: str = "dometic"
    discovery: bool = True
    discovery_prefix: str = "homeassistant"


@dataclass
class Config:
    thermostat: ThermostatCfg = field(default_factory=ThermostatCfg)
    protections: ProtectionsCfg = field(default_factory=ProtectionsCfg)
    sensors: SensorsCfg = field(default_factory=SensorsCfg)
    pins: PinsCfg = field(default_factory=PinsCfg)
    api: ApiCfg = field(default_factory=ApiCfg)
    loop: LoopCfg = field(default_factory=LoopCfg)
    mqtt: MqttCfg = field(default_factory=MqttCfg)


_cached: Config | None = None
_cached_mtime: float = 0.0


def load_config(force: bool = False) -> Config:
    """Load config; reload if the file changed on disk."""
    global _cached, _cached_mtime
    path = _default_config_path()
    mtime = path.stat().st_mtime
    if not force and _cached is not None and mtime == _cached_mtime:
        return _cached
    cfg = Config()
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    for section in ("thermostat", "protections", "sensors", "pins",
                     "api", "loop", "mqtt"):
        if section in data:
            cls = getattr(cfg, section).__class__
            setattr(cfg, section, cls(**data[section]))
    _cached = cfg
    _cached_mtime = mtime
    return cfg
