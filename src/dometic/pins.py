"""Pin-name to BCM GPIO number mapping."""
from dometic.config import Config


def get_pin_map(cfg: Config) -> dict:
    return {
        "FAN_LOW":   cfg.pins.fan_low,
        "FAN_HIGH":  cfg.pins.fan_high,
        "COOL":      cfg.pins.cool,
        "HEAT_PUMP": cfg.pins.heat_pump,
        "FURNACE":   cfg.pins.furnace,
        "COMP1":     cfg.pins.comp1,
        "COMP2":     cfg.pins.comp2,
        "RV1":       cfg.pins.rv1,
        "RV2":       cfg.pins.rv2,
        "INTERSTG":  cfg.pins.interstage,
        "SPARE1":    cfg.pins.spare1,
        "SPARE2":    cfg.pins.spare2,
    }
